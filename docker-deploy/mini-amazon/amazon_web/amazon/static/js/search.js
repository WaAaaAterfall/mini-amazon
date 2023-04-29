// Get the search form and input field
const searchForm = document.querySelector('#search-form');
const searchInput = document.querySelector('#search-input');

// Add an event listener to the form
searchForm.addEventListener('submit', (event) => {
  // Prevent the default form submission behavior
  event.preventDefault();
  

  // Construct the search URL using the value of the input field
  const user_type = searchInput.value;
  const searchUrl = `/amazon/search/${user_type}/`;

  // Redirect the user to the search results page
  window.location.replace(searchUrl);
});
