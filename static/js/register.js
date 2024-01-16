$(document).ready(function() {
    spinner(0)
    $('#register-form').submit(function(event) {
        event.preventDefault();
        // Create FormData from the form
        var formData = new FormData(this);
        var password = $('#password').val()
        var confirm_password =  $('#confirm-password').val()
        spinner(1)
        if (password===confirm_password){
        // Send a POST request to /register using fetch
            fetch('/register', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => { // Log the response from /register
                spinner(0) 
                // console.log(data)
                if (data['msg'] === "Email Alredy Registered"){
                    alert("Email alredy Registered! Login Instead")
                }
                else if (data['msg']==="Internel Error"){
                    alert("Internel Error Please try again")
                }
                else if (data["msg"]==="Invalid OTP"){
                    alert("Invalid OTP!")
                }
                else if (data["msg"]==="Time Exceeded"){
                    alert("Time exceeded. Generate New OTP")
                }    
                else if (data["msg"]==="Success"){
                    alert("Success! Login Please")
                    window.location.href="/login"
                }
                       
            })
            .catch(error => {
                console.error('Error during fetch:', error);
                spinner(0)  
            });
        }else{
            alert("Passwords Mismatch. Try Again")
            spinner(0)
        }    
    });
    $('#sendOTP').click(function() {   //For Sending OTP
        var email = $('#email').val();
        $('#otp').val("");
        spinner(1)
        $.ajax({
            url: '/sendotp',
            method: 'GET',
            data: {
                email: email
            },
            success: function(response) {
              spinner(0)
                if (response === true){
                    alert("Otp sent! Please Check Your Email")
                }
                else{
                alert(response.message)
                }
            },
            error: function(error) {
                spinner(0)
                console.log('Error:', error);
            }
        });
    });
});
  
function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password");
    var toggleIcon = document.querySelector(".toggle-password i");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.classList.remove("fa-eye");
        toggleIcon.classList.add("fa-eye-slash");
    } else {
        passwordInput.type = "password";
        toggleIcon.classList.remove("fa-eye-slash");
        toggleIcon.classList.add("fa-eye");
    }
}
  
function spinner(val) {
if (val === 1) {
    $('#loadingSpinner').removeClass('d-none');
} else if (val === 0) {
    $('#loadingSpinner').addClass('d-none');
}
}