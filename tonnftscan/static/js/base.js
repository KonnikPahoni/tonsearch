function performSearch() {
    const query = document.getElementById('searchInput').value;

    window.location.href = siteUrl + '/search?query=' + encodeURIComponent(query);
}


document.addEventListener("DOMContentLoaded", function () {
    var input = document.getElementById('searchInput');

    // Execute a function when the user presses a key on the keyboard
    input.addEventListener("keypress", function (event) {
        // If the user presses the "Enter" key on the keyboard
        if (event.key === "Enter") {
            // Cancel the default action, if needed
            event.preventDefault();
            // Trigger the button element with a click
            document.getElementById("searchButton").click();
        }
    });
});