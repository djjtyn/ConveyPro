//This file contains JS relevant to all pages within the application
$(document).ready(() => {
    initDevelopmentSelector();
});

function initDevelopmentSelector() {
    $('#developmentSelector').on('change', function () {
        const selectedDevelopment = $(this).find(':selected').val();
        redirectUser(selectedDevelopment)
    })
}

//Get the current url, replace the current selected development and redirect
function redirectUser(development) {
    const currentURL = window.location.href;
    const urlComponents = currentURL.split('/');
    //The development value resides at index 3 of the currentURL array
    urlComponents[3] = development;
    //Redirect to the list of active opportunities for the selected development
    if(currentURL.includes('properties') && urlComponents[urlComponents.length - 1] != 'properties') {
        //If the user is on a specific listing remove the final array index id and redirect to parent development listings page
        urlComponents.pop();
    }
    const targetURL = urlComponents.join('/');
    window.location = targetURL;
}