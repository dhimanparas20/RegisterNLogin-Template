$(document).ready(function() {
  spinner(0)
  $('#login-form').submit(function(event) {
    event.preventDefault();
    var formData = new FormData(this); 
    spinner(1)
    fetch('/login', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      spinner(0)  // Log the response from /login
      // console.log(data)
      if (data['msg']==="Success"){
        window.location.href="/"
      }
      else if (data['msg']==="Invalid Credentials"){
        alert("Invalid Credentails")
      }
    })
    .catch(error => {
      spinner(0)
      console.error('Error during fetch:', error);
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