//This file contains JS relevant to all authentication pages within the application
$(document).ready(() => {
    //If registration form exists, handle its override its default submit
    if($('#registrationForm').length) {
        initRegistrationFormHandler()
    }
});


function initRegistrationFormHandler() {
    //If registration form exists ensure it isn't submit with a password mismatch
    $('#registrationForm').on('submit', function (e) {
        e.preventDefault();
        passwordOne = $('#id_password').val();
        passwordTwo = $('#id_password_confirmation').val();
        //If both passwords match submit the form, otherwise display message to user 
        if (passwordsMatch(passwordOne, passwordTwo)) {
            this.submit();
        } else {
            notifyUser('passwordMismatch')
        }
    })
}

function passwordsMatch(valOne, valTwo) {
    console.log(valOne == valTwo);
    return valOne == valTwo;
}

function notifyUser(notificationType) {
    if (notificationType == 'passwordMismatch') {
        $('#passwordError').removeAttr('hidden');
        $('#passwordError').text('Provided Passwords do not Match');
        //Change bg color of the passwords to red
        $('#registrationForm input[type=password').each((i, element)=>{
            $(element).css('background-color', 'red');
        });
    }
}
