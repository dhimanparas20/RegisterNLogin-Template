import requests
import configparser as cp

# Load configuration file
cfg = cp.ConfigParser()
cfg.read('Configs/config.conf')

GMAIL_ADDRESS = cfg['BREVO']['GMAIL_ADDRESS']
GMAIL_NAME = cfg['BREVO']['GMAIL_Name']
BREVO_API = cfg['BREVO']['BREVO_API']

def sendOTP(address,otp):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API,
        "content-type": "application/json"
    }
    payload = {
        "sender": {
            "name": GMAIL_NAME,
            "email": GMAIL_ADDRESS
        },
        "to": [
            {
                "email": address,
            }
        ],
        "subject": "OTP Verification",
        "htmlContent": f'''<!DOCTYPE html>
                            <html>
                            <head>
                                <title>OTP Verification</title>
                            </head>
                            <body>
                                <h3>OTP Verification</h3>
                                <p>Hello USER,</p>
                                <p>Your One-Time Password (OTP) for verification is: <strong>{otp}</strong></p>
                                <p>Please use this OTP to complete your verification process. This OTP will expire in 30 minutes.</p>
                                <p>If you did not request this OTP, please ignore this email.</p>
                                <p>Thank you for using our service!</p>
                                <p>Best regards,<br>MST Services</p>
                            </body>
                            </html>
                        ''' 
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in range (200,299):
        return True
    else:
        #print("Email sending failed")
        return False