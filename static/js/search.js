// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const typeSelect = document.getElementById('typeSelect');
    const searchForm = document.getElementById('searchForm');
    const enquireButton = document.getElementById('enquireButton');
    const enquiryForm = document.getElementById('enquiryForm');
    const checkboxes = document.querySelectorAll('.item-checkbox');
    
    // Add event listener for type select
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            // Automatically submit form when type changes
            searchForm.submit();
        });
    }
    
    // Add loading indicator to search button
    const searchButton = document.querySelector('.search-button');
    if (searchForm && searchButton) {
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
    }
    
    // Handle checkboxes and enquire button
    if (checkboxes.length > 0 && enquireButton) {
        // Add event listeners to all checkboxes
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', updateEnquireButton);
        });
        
        // Initial update of enquire button state
        updateEnquireButton();
        
        // Handle enquire button click
        enquireButton.addEventListener('click', function() {
            if (hasCheckedItems()) {
                enquiryForm.submit();
            }
        });
    }
    
    // Function to check if any items are checked
    function hasCheckedItems() {
        return Array.from(checkboxes).some(checkbox => checkbox.checked);
    }
    
    // Function to update enquire button state
    function updateEnquireButton() {
        if (hasCheckedItems()) {
            enquireButton.disabled = false;
            enquireButton.classList.add('active');
        } else {
            enquireButton.disabled = true;
            enquireButton.classList.remove('active');
        }
    }
});