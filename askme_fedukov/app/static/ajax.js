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

like_active = `\
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-circle-fill" viewBox="0 0 16 16">
  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M8.5 4.5a.5.5 0 0 0-1 0v3h-3a.5.5 0 0 0 0 1h3v3a.5.5 0 0 0 1 0v-3h3a.5.5 0 0 0 0-1h-3z"/>
</svg>
`
like_inactive = `\
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-circle" viewBox="0 0 16 16">
  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
  <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
</svg>
`
dislike_inactive = `\
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-dash-circle" viewBox="0 0 16 16">
  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
  <path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8"/>
</svg>
`
dislike_active = `\
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-dash-circle-fill" viewBox="0 0 16 16">
  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M4.5 7.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1z"/>
</svg>
`


function likeCard(like_type, like_action, card_id, card_type) {

    axios.post('/like/', {
        like_type: like_type,
        like_action: like_action
    }, {
        params: {
            id: card_id,
            model_type: card_type
        }
    })
        .then(function (response) {
            // Handle the response data
            // Example: update like/dislike button UI dynamically
            if (response.data && typeof response.data.like_status !== "undefined") {
                const cardId = response.data.card_id;
                const likeContainer = document.querySelector(`div[data-card-id="${cardId}"]`);
                if (likeContainer) {
                    const likeBtn = likeContainer.querySelector("button[data-like-btn]");
                    const dislikeBtn = likeContainer.querySelector("button[data-dislike-btn]");
                    if (likeBtn && dislikeBtn) {
                        // Reset all
                        likeBtn.removeAttribute("data-isActive");
                        dislikeBtn.removeAttribute("data-isActive");
                        likeBtn.classList.remove("btn-success", "text-success", "text-muted");
                        dislikeBtn.classList.remove("btn-danger", "text-danger", "text-muted");
                        // Remove all icon classes for plus/dash
                        const likeIcon = likeBtn.querySelector("svg");
                        const dislikeIcon = dislikeBtn.querySelector("svg");
                        if (likeIcon) {
                            likeIcon.classList.remove(
                                "bi-plus-circle", "bi-plus-circle-fill",
                                "text-success", "text-muted"
                            );
                        }
                        if (dislikeIcon) {
                            dislikeIcon.classList.remove(
                                "bi-dash-circle", "bi-dash-circle-fill",
                                "text-danger", "text-muted"
                            );
                        }

                        if (response.data.like_status === 1) {
                            // Liked
                            likeBtn.setAttribute("data-isActive", "");
                            likeBtn.classList.add("btn-success", "text-success");
                            if (likeIcon) {
                                likeIcon.classList.add("bi-plus-circle-fill", "text-success");
                                likeIcon.classList.remove("bi-plus-circle", "text-muted");
                            }
                            dislikeBtn.classList.add("text-muted");
                            if (dislikeIcon) {
                                dislikeIcon.classList.add("bi-dash-circle", "text-muted");
                                dislikeIcon.classList.remove("bi-dash-circle-fill", "text-danger");
                            }
                        } else if (response.data.like_status === -1) {
                            // Disliked
                            dislikeBtn.setAttribute("data-isActive", "");
                            dislikeBtn.classList.add("btn-danger", "text-danger");
                            if (dislikeIcon) {
                                dislikeIcon.classList.add("bi-dash-circle-fill", "text-danger");
                                dislikeIcon.classList.remove("bi-dash-circle", "text-muted");
                            }
                            likeBtn.classList.add("text-muted");
                            if (likeIcon) {
                                likeIcon.classList.add("bi-plus-circle", "text-muted");
                                likeIcon.classList.remove("bi-plus-circle-fill", "text-success");
                            }
                        } else {
                            // Neutral
                            likeBtn.classList.add("text-muted");
                            dislikeBtn.classList.add("text-muted");
                            if (likeIcon) {
                                likeIcon.classList.add("bi-plus-circle", "text-muted");
                                likeIcon.classList.remove("bi-plus-circle-fill", "text-success");
                            }
                            if (dislikeIcon) {
                                dislikeIcon.classList.add("bi-dash-circle", "text-muted");
                                dislikeIcon.classList.remove("bi-dash-circle-fill", "text-danger");
                            }
                        }
                        // Optionally update likes count
                        const likesLabel = likeContainer.querySelector("[data-likes-value]");
                        if (likesLabel && typeof response.data.like_count !== "undefined") {
                            likesLabel.textContent = response.data.like_count;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            console.error('Error liking card:', error);
        });
}


function getActonForActive(btn) {
    return btn.getAttribute("data-isActive") == null ? "put" : "delete";
}

function main() {
    // All axios requests will have csrf token in headers
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

    // Handle like and dislike buttons
    document.querySelectorAll("div[data-like-container]").forEach(function (likeContainer) {
        const card_id = likeContainer.getAttribute("data-card-id");
        const card_type = likeContainer.getAttribute("data-card-type");

        const like_btn = likeContainer.querySelector("button[data-like-btn]");
        const dislike_btn = likeContainer.querySelector("button[data-dislike-btn]");

        like_btn.addEventListener("click", function (btn) {
            likeCard("like", getActonForActive(btn.currentTarget), card_id, card_type);
        });

        dislike_btn.addEventListener("click", function (btn) {
            likeCard("dislike", getActonForActive(btn.currentTarget), card_id, card_type);
        });
    })

}


document.addEventListener('DOMContentLoaded', main)
