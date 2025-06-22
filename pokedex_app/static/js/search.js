document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const searchResultsModal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
    
    // Handle search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const query = searchInput.value.trim();
            if (query.length < 2) {
                return;
            }
            
            // Fetch search results
            fetch(`/search?q=${encodeURIComponent(query)}&limit=10`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data);
                })
                .catch(error => {
                    console.error('Error searching:', error);
                    searchResults.innerHTML = '<p class="text-danger">An error occurred while searching. Please try again.</p>';
                });
        });
    }
    
    // Search input autocomplete
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = searchInput.value.trim();
            
            if (query.length < 2) {
                return;
            }
            
            // Fetch search suggestions
            fetch(`/search?q=${encodeURIComponent(query)}&limit=5`)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        displaySearchResults(data);
                        searchResultsModal.show();
                    }
                })
                .catch(error => {
                    console.error('Error getting suggestions:', error);
                });
        }, 300));
    }
    
    // Display search results in the modal
    function displaySearchResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = '<p class="text-center">No Pokémon found. Try a different search term.</p>';
        } else {
            let html = '<div class="list-group">';
            
            results.forEach(pokemon => {
                html += `
                    <a href="/pokemon/${pokemon.id}" class="list-group-item list-group-item-action">
                        <div class="d-flex align-items-center">
                            <img src="${pokemon.sprite}" alt="${pokemon.name}" class="me-3" style="width: 50px; height: 50px;">
                            <div>
                                <div class="d-flex align-items-center">
                                    <span class="text-muted me-2">#${String(pokemon.id).padStart(3, '0')}</span>
                                    <strong>${pokemon.name}</strong>
                                </div>
                                <div class="pokemon-types">
                                    ${pokemon.types.map(type => `<span class="type-badge type-${type.toLowerCase()}">${type}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    </a>
                `;
            });
            
            html += '</div>';
            searchResults.innerHTML = html;
        }
        
        searchResultsModal.show();
    }
    
    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}); 