// Add a listener to the route box if the user presses enter rather than
// clicking the "Apply" button to enter the routes.
document.getElementById("routeBox").addEventListener("keydown", function(event) {
  // Check if the key pressed is "Enter"
  if (event.key === "Enter") {
    // Prevent the default behavior (if any)
    event.preventDefault();
    // Accept the string with the same function the "Apply" button uses.
    applyRoutes();
  }
});

