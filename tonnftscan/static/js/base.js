function performSearch() {
    // Get the input value
    var query = document.getElementById('searchInput').value;

    // Build the URL with the query parameter
    var searchUrl = 'http://localhost:8008/search?query=' + encodeURIComponent(query);

    // Redirect to the search page
    window.location.href = searchUrl;
}


document.addEventListener("DOMContentLoaded", function() {
    var input = document.getElementById('searchInput');

    // Execute a function when the user presses a key on the keyboard
    input.addEventListener("keypress", function(event) {
        // If the user presses the "Enter" key on the keyboard
        if (event.key === "Enter") {
            // Cancel the default action, if needed
            event.preventDefault();
            // Trigger the button element with a click
            document.getElementById("searchButton").click();
        }
    });
});