// Get the search input and dropdown elements
const searchInput = document.getElementById('search-input');
const searchDropdown = document.getElementById('search-dropdown');

// Mock data for search results
const mockData = [
  'Barbells',
  'Kettlebells',
  'Weight plates',
  'Medicine balls',
  'Weighted vests',
  'Ankle Weights',
  'Weighted Bars',
  'Weighted Resistance bars',
  'Sport Bras',
  'Sport shoes',
  'Sport Shorts',
  'Tshirts',
  'Leggings',
  'Sport Headbands',
  'Accessories',
  'Exercise Mats'
];

// Function to show the dropdown with search results
function showDropdown() {
  searchDropdown.style.display = 'block';
}

// Function to hide the dropdown
function hideDropdown() {
  searchDropdown.style.display = 'none';
}

// Function to filter search results based on input
function filterResults() {
  const inputValue = searchInput.value.toLowerCase();
  const filteredResults = mockData.filter(item => item.toLowerCase().includes(inputValue));
  displayResults(filteredResults);
}

// Function to display search results in the dropdown
function displayResults(results) {
  // Clear existing dropdown items
  searchDropdown.innerHTML = '';

  if (results.length === 0) {
    const noResultsItem = document.createElement('div');
    noResultsItem.textContent = 'No results found';
    noResultsItem.classList.add('search-dropdown-item');
    searchDropdown.appendChild(noResultsItem);
  } else {
    results.forEach(result => {
      const dropdownItem = document.createElement('div');
      dropdownItem.textContent = result;
      dropdownItem.classList.add('search-dropdown-item');
      dropdownItem.addEventListener('click', () => {
        searchInput.value = result;
        hideDropdown();
      });
      searchDropdown.appendChild(dropdownItem);
    });
  }
}

// Event listeners for input and focus events
searchInput.addEventListener('input', () => {
  showDropdown();
  filterResults();
});
searchInput.addEventListener('focus', showDropdown);
searchInput.addEventListener('blur', hideDropdown);
