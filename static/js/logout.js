// Our function to use to submit the logout form.
function submitLogoutForm(event) {
    event.preventDefault();
    document.getElementById('logout-form').submit();
};

window.submitLogoutForm = submitLogoutForm;
