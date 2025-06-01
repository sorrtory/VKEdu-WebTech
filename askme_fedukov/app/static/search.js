document.addEventListener("DOMContentLoaded", function() {
    
    // Add event listener for the search input
    const searchInput = document.getElementById("ask-input");
    const searchContainer = document.getElementById("search-results-container");

    // Hide the search results when clicking outside the input
    document.addEventListener("click", function(event) {
        if (!searchInput.contains(event.target) && !searchContainer.contains(event.target)) {
            searchContainer.style.display = "none";
        } else {
            searchContainer.style.display = "block";
        }
    }
    );

    
    if (searchInput) {
        searchInput.addEventListener("input", function() {
            const query = searchInput.value;
            
            if (query.length === 0) {
                // Clear results if input is empty
                searchContainer.style.display = "none";
                return;
            } else {
                searchContainer.style.display = "block";
            }

            axios.post("/search/", {
                query: query
            })
            .then(function(response) {
                const results = response.data.results;
                const resultsContainer = document.getElementById("search-results");

                // Update the results count
                const resultsCount = document.getElementById("search-results-count");
                resultsCount.textContent = results.length;
                
                // Clear previous results
                resultsContainer.innerHTML = "";
                // Display new results
                if (results.length > 0) {
                    results.forEach(function(result) {
                        const resultItem = document.createElement("li");
                        resultItem.className = "result-item";
                        resultItem.innerHTML = `<a href="/question/${result.id}">${result.title}</a>`;
                        resultsContainer.appendChild(resultItem);
                    });
                } else {
                    resultsContainer.innerHTML = "<p>No results found.</p>";
                }
            })
            .catch(function(error) {
                console.error("Error fetching search results:", error);
                const resultsContainer = document.getElementById("search-results");
                resultsContainer.innerHTML = "<p>Error fetching results. Please try again later.</p>";
            });


        });
    }
});