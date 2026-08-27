// Extracted from templates/bookings/service_request_list.html
document.addEventListener('DOMContentLoaded', function() {
    const filterTags = document.querySelectorAll('.filter-tag');
    const searchInput = document.getElementById('searchInput');
    const requestCards = document.querySelectorAll('.request-card');

    function filterRequests() {
        const activeFilter = document.querySelector('.filter-tag.active').dataset.filter;
        const searchTerm = searchInput.value.toLowerCase();

        requestCards.forEach(card => {
            const status = card.dataset.status;
            const text = card.textContent.toLowerCase();
            
            let statusMatch = activeFilter === 'all' || status.includes(activeFilter);
            let searchMatch = text.includes(searchTerm);

            if (statusMatch && searchMatch) {
                card.style.display = '';
                card.style.animation = 'fadeIn 0.3s ease';
            } else {
                card.style.display = 'none';
            }
        });
    }

    filterTags.forEach(tag => {
        tag.addEventListener('click', function() {
            filterTags.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            filterRequests();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', filterRequests);
    }
});

// Add fadeIn animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
