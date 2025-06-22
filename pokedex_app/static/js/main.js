/**
 * Pokédex Web Application Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        Array.from(tooltips).forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }

    // Sticky header effect
    const header = document.querySelector('header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('header-scrolled');
            } else {
                header.classList.remove('header-scrolled');
            }
        });
    }

    // Card hover effects
    const cards = document.querySelectorAll('.pokemon-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover');
        });
    });

    // Apply animations to hero elements when page loads
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroButtons = document.querySelectorAll('.hero-section .btn');
    const heroImage = document.querySelector('.hero-image');
    
    if (heroTitle) {
        setTimeout(() => {
            heroTitle.classList.add('animate__animated', 'animate__fadeInUp');
        }, 300);
    }
    
    if (heroSubtitle) {
        setTimeout(() => {
            heroSubtitle.classList.add('animate__animated', 'animate__fadeInUp');
        }, 500);
    }
    
    if (heroButtons.length) {
        setTimeout(() => {
            heroButtons.forEach((btn, index) => {
                btn.classList.add('animate__animated', 'animate__fadeInUp');
                btn.style.animationDelay = `${0.7 + (index * 0.2)}s`;
            });
        }, 700);
    }
    
    if (heroImage) {
        setTimeout(() => {
            heroImage.classList.add('animate__animated', 'animate__fadeIn');
        }, 1000);
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href !== "#") {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    window.scrollTo({
                        top: target.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Add animation to elements when they come into view
    function animateOnScroll() {
        const elements = document.querySelectorAll('.feature-card, .pokemon-card, .section-header, .generation-info');
        
        elements.forEach(element => {
            if (isInViewport(element) && !element.classList.contains('animated')) {
                element.classList.add('animated', 'animate__animated', 'animate__fadeInUp');
            }
        });
    }

    // Call once on load
    animateOnScroll();
    
    // Attach to scroll event
    window.addEventListener('scroll', animateOnScroll);

    // Team Builder placeholder functionality
    const teamBuilderLinks = document.querySelectorAll('#teamBuilderLink, #teamBuilderFooterLink');
    teamBuilderLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Team Builder feature coming soon!');
        });
    });

    // Generation theme switching - for demo purposes only
    const themeToggleButtons = document.querySelectorAll('[data-theme-toggle]');
    themeToggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const themeId = this.getAttribute('data-theme-toggle');
            
            // Here you would usually make an API call to get the theme
            // For demo purposes, we're just changing the CSS variables directly
            
            // Sample theme colors for demonstration
            const themes = {
                '1': { primary: '#FF0000', secondary: '#0000FF', accent: '#FFD700' },  // Gen 1 (Kanto)
                '2': { primary: '#DAA520', secondary: '#C0C0C0', accent: '#4FD9FF' },  // Gen 2 (Johto)
                '3': { primary: '#A00000', secondary: '#0000A0', accent: '#00A000' },  // Gen 3 (Hoenn)
                '4': { primary: '#AAA9AD', secondary: '#DDADBB', accent: '#999999' },  // Gen 4 (Sinnoh)
                '5': { primary: '#2C2C2C', secondary: '#E8E8E8', accent: '#7D7D7D' },  // Gen 5 (Unova)
                '6': { primary: '#025DA6', secondary: '#EA1A3E', accent: '#F1D302' },  // Gen 6 (Kalos)
                '7': { primary: '#F1912B', secondary: '#5599CA', accent: '#D1D1E0' },  // Gen 7 (Alola)
                '8': { primary: '#00A1E9', secondary: '#BF004F', accent: '#C6B404' },  // Gen 8 (Galar)
                '9': { primary: '#E3350D', secondary: '#7700FF', accent: '#FFCB05' }   // Gen 9 (Paldea)
            };
            
            if (themes[themeId]) {
                document.documentElement.style.setProperty('--primary-color', themes[themeId].primary);
                document.documentElement.style.setProperty('--secondary-color', themes[themeId].secondary);
                document.documentElement.style.setProperty('--accent-color', themes[themeId].accent);
                
                // Update navbar color
                document.querySelector('.navbar').style.backgroundColor = themes[themeId].primary;
                
                // You would also update other theme-specific elements here
            }
        });
    });
    
    // Add scroll-to-top button functionality
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('show');
            } else {
                scrollToTopBtn.classList.remove('show');
            }
        });
        
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Pokemon comparison functionality
    const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
    const compareButton = document.getElementById('compareButton');
    
    if (compareCheckboxes.length > 0 && compareButton) {
        compareCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateCompareButton);
        });
        
        // Update compare button state initially
        updateCompareButton();
    }
    
    function updateCompareButton() {
        const selectedPokemon = Array.from(document.querySelectorAll('.compare-checkbox:checked')).map(
            checkbox => checkbox.getAttribute('data-pokemon-id')
        );
        
        if (selectedPokemon.length >= 2 && selectedPokemon.length <= 3) {
            compareButton.classList.remove('disabled');
            compareButton.href = `/pokemon/compare?ids=${selectedPokemon.join(',')}`;
        } else {
            compareButton.classList.add('disabled');
            compareButton.href = '#';
        }
    }
}); 