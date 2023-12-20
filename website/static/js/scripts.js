const cancelBtn = document.getElementById("cancel-button");

if (cancelBtn) {
  cancelBtn.addEventListener("click", () => {
    // navigate to home page
    window.location.href = "/home/";
  });
}



// Assuming your search results are stored in a variable named `searchResults`
const searchResultsHeader = document.querySelector("#search-results-header");

// Check if there are search results
if (searchResults && searchResults.length > 0) {
  searchResultsHeader.style.visibility = "visible";
} else {
  searchResultsHeader.style.visibility = "hidden";
}



// const searchResultsHeader = document.querySelector("#search-results-header");
// const searchButton = document.querySelector("#search-btn-search-page");

// if (searchButton) {
//   searchButton.addEventListener("click", () => {
//     searchResultsHeader.style.visibility = "visible";
//   });
// }
