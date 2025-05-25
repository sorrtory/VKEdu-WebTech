function name(params) {
    axios.get('/profile/0/', {
        params: {
            id: 12345
        }
    })
    .then(function (response) {
        console.log(response);
    })
    .catch(function (error) {
        console.log(error);
    })
    .finally(function () {
        console.log('Request completed');
    });
}

function main() {
    // All axios requests will have csrf token in headers
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");


}


document.addEventListener('DOMContentLoaded', main)
    