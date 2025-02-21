// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const typeSelect = document.getElementById('typeSelect');
    const searchForm = document.getElementById('searchForm');
    
    // Add event listener for type select
    typeSelect.addEventListener('change', function() {
        // Automatically submit form when type changes
        searchForm.submit();
    });
    
    // Add loading indicator to search button
    const searchButton = document.querySelector('.search-button');
    searchForm.addEventListener('submit', function() {
        searchButton.textContent = 'Searching...';
        searchButton.style.backgroundColor = '#999';
        searchButton.disabled = true;
        
        // Reset button after short delay (in case of quick response)
        setTimeout(function() {
            searchButton.textContent = 'Search';
            searchButton.style.backgroundColor = '';
            searchButton.disabled = false;
        }, 2000);
    });
});
