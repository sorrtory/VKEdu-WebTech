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

    document.querySelectorAll('.ajax-link').forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const url = this.getAttribute('href');
            axios.get(url)
                .then(function (response) {
                    // Handle the response data
                    console.log(response.data);
                })
                .catch(function (error) {
                    // Handle the error
                    console.error(error);
                });
        });
    })

    // Handle like and dislike buttons
    document.querySelectorAll("div[data-like-container]").forEach(function (likeContainer) {
        card_id = likeContainer.getAttribute("data-card-id");
        card_type = likeContainer.getAttribute("data-card-type");
        
        like_btn = likeContainer.querySelector("button[data-like-btn]");
        dislike_btn = likeContainer.querySelector("button[data-dislike-btn]");


    })

}


document.addEventListener('DOMContentLoaded', main)
    