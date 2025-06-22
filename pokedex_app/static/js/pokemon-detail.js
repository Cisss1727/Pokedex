/**
 * Pokemon Detail Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Using a lower max value for better visual representation
    // Highest base stat in Pokemon is around 150-180, so we'll use 180 for better visuals
    const MAX_STAT = 180;
    
    // Initialize stat bars with animation and percentage
    function initializeStatBars() {
        const statBars = [
            { id: 'hpBar' },
            { id: 'attackBar' },
            { id: 'defenseBar' },
            { id: 'spAtkBar' },
            { id: 'spDefBar' },
            { id: 'speedBar' }
        ];

        statBars.forEach(barInfo => {
            const bar = document.getElementById(barInfo.id);
            if (bar) {
                bar.style.width = '0%';
                bar.style.display = 'block';
            }
        });

        setTimeout(() => {
            statBars.forEach(barInfo => {
                const bar = document.getElementById(barInfo.id);
                if (bar) {
                    const value = parseInt(bar.getAttribute('data-value'));
                    const percent = Math.round((value / MAX_STAT) * 100);
                    bar.style.width = Math.min(percent, 100) + '%';
                }
            });
        }, 50);
    }
    
    // Initialize when DOM is loaded
    initializeStatBars();
    
    // Shiny toggle functionality
    const shinyToggle = document.getElementById('shinyToggle');
    const pokemonImage = document.getElementById('pokemonImage');
    
    if (shinyToggle && pokemonImage) {
        let isShiny = false;
        const normalImage = pokemonImage.src;
        const shinyImage = normalImage.replace('/hires/', '/shiny/');
        
        shinyToggle.addEventListener('click', function() {
            if (isShiny) {
                pokemonImage.src = normalImage;
                shinyToggle.classList.remove('active');
            } else {
                pokemonImage.src = shinyImage;
                shinyToggle.classList.add('active');
            }
            isShiny = !isShiny;
        });
    }
}); 