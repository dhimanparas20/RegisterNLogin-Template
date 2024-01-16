from flask import Flask, render_template,make_response,request, session, redirect
from authlib.integrations.flask_client import OAuth
from flask_restful import Api, Resource
from flask_session import Session
from datetime import datetime
from sendMail import sendOTP
from pyMongo import MongoDB
import configparser as cp
from os import environ,system
import secrets
import uuid
import random
system("clear")

# Load configuration file
cfg = cp.ConfigParser()
cfg.read('Configs/config.conf')

# Get environment variables using os.environ.get
CLIENT_ID = environ.get('CLIENT_ID') or cfg['GOOGLE']['CLIENT_ID']
CLIENT_SECRET = environ.get('CLIENT_SECRET') or cfg['GOOGLE']['CLIENT_SECRET']
MONGO_CLIENT  = cfg['DB']['MONGO_CONNECTION_STRING']
USE_LOCAL_DB = cfg['DB'].getboolean('USE_LOCAL_DB')  # True if wanna use cloud DB

def generate_secure_user_key():
    user_key = secrets.token_hex(16)  # Adjust the length as needed
    return user_key
def generate_user_key():
    # Generate a UUID version 4 (randomly generated) as a string
    user_key = str(uuid.uuid4())
    return user_key

app = Flask(__name__)
api = Api(app)

#Databases
if USE_LOCAL_DB == False:
    dbuser = MongoDB("MST","users",MONGO_CLIENT) #{"id":"","name":"","email":"","password":""}
    dbtemp = MongoDB("MST","temp",MONGO_CLIENT) #
else:
    dbuser = MongoDB("MST","users") 
    dbtemp = MongoDB("MST","temp") #

app.config['SECRET_KEY'] = "c365a380254da310e47c24a692dad2e8"
app.config['SESSION_TYPE'] = 'filesystem'  #Sessions are stored as files on the server.(development only)
app.config['SESSION_PERMANENT'] = False #False -> session will expire when the browser is closed.
app.config['SESSION_USE_SIGNER'] = True  # adds a cryptographic signature to the session cookie 
app.config['SESSION_COOKIE_SAMESITE'] = 'None' #cookies will be sent with cross-origin requests.
app.config['SESSION_COOKIE_SECURE'] = True #ensures that the session cookie is only sent over HTTPS connections.

Session(app)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

def generate_otp():
    # Generate a random 6-digit number
    otp = random.randint(100000, 999999)
    return otp

#Dashboard
class Home(Resource):
    def get(self):
        id = session.get('id')
        if id:
            return ({"id":id,"msg":"You are logged in"})
        else:
           return redirect("/login")

# Registration
class Register(Resource):
    def get(self):
        return make_response(render_template('register.html'))
    
    def post(self):
        data = request.form.to_dict() 
        otp = data['otp']
        current_datetime = datetime.now()
        combined_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
        tempdbdata = dbtemp.fetch({"email":data["email"]})
        if tempdbdata != [] and int(combined_datetime)-tempdbdata[0]['timestamp']<=3000:
            if int(otp) == tempdbdata[0]['otp']:
                dbtemp.delete({"email":data["email"]})
                check = dbuser.fetch({"email":data['email']})
                if check == []:
                    insertdata = {"id":generate_user_key(),"name":data['name'],"email":data['email'],"password":dbuser.hashit(data['password'])}
                    status  = dbuser.insert(insertdata)
                    if status == True:
                      return({"msg":"Success"})
                    return ({"msg":"Internel Error"})
                return({"msg":"Email Alredy Registered"})  
            return({"msg":"Invalid OTP"})  
        return({"msg":"Time Exceeded"})  
        # access_token = create_access_token(identity=data['email']) # lets not use JWT for now
 
# Normal Login
class Login(Resource):
    def get(self):
        return make_response(render_template('login.html'))
    
    def post(self):
        data = request.form.to_dict()
        res =  dbuser.fetch({"email":data["email"]}) 
        if res != []:
           hashpass = res[0]["password"]
           allow = dbuser.verifyHash(data["password"],hashpass)
           if allow == True:
              session['id'] = res[0]["id"]
              return ({"msg":"Success"})   
        return ({"msg":"Invalid Credentials"})   
        
# Sends otp During Registration  "/sendotp"
class SendOtp(Resource):
    def get(self):
        email = request.args.get('email')
        current_datetime = datetime.now()  # Current date and time
        combined_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
        otp = generate_otp()
        data = {"email":email,"otp":otp,"timestamp":int(combined_datetime)}
        dbdata = dbtemp.fetch({"email":email})
        if dbdata == []:
            resp = dbtemp.insert(data)
        else:
            resp = dbtemp.update({"email":email},data)  
        result = sendOTP(email,otp)
        if resp ==  True and result == True:
            return True
        return False        

#Login/Register Using google
class GoogleLogin(Resource):
    def get(self):
        return google.authorize_redirect(redirect_uri=api.url_for(AuthorizedResource, _external=True, _method='GET'))

# AuthorizedResource
class AuthorizedResource(Resource):
    def get(self):
        token = google.authorize_access_token()
        user_info = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        data = user_info.json()
        id = data["id"]
        name = data["name"]
        email = data["email"]
        password =  dbuser.hashit(id)
        res = dbuser.fetch({"id":id})
        if res != []:
            session['id'] = id
            return redirect("/")
        insertdata = {"id":id,"name":name,"email":email,"password":password}    
        resp = dbuser.insert(insertdata)
        if resp ==  True:
            session['id'] = id
            return redirect("/")
        return redirect("/register")

#Logout
class Logout(Resource):
    def get(self):
      id = session.get('id')
      if 'id' in session:
        session.pop('id', None)  # Remove user_id from session
        return redirect("/login")
      else:
        return redirect("/login")


api.add_resource(Home, '/')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(GoogleLogin, '/googlelogin')
api.add_resource(AuthorizedResource, '/AuthorizedResource')
api.add_resource(SendOtp, '/sendotp')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
    app.run(debug=True)
