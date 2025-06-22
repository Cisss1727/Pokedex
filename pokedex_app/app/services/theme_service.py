from pokedex_app.app.models.mongodb import mongo
from flask_caching import Cache
from flask import current_app

def get_generation_theme(generation):
    """
    Returns theme data for the specified generation.
    
    Args:
        generation (int): Pokemon generation number (1-9)
        
    Returns:
        dict: Theme data including CSS file, colors, and title
    """
    themes = {
        1: {
            'css_file': 'themes/gen1.css',
            'primary_color': '#ff1111',  # Red version
            'secondary_color': '#0000FF',  # Blue version
            'title': 'Kanto',
            'description': 'Generation I introduced the world to Pokemon Red and Blue versions.'
        },
        2: {
            'css_file': 'themes/gen2.css',
            'primary_color': '#daa520',  # Gold version
            'secondary_color': '#c0c0c0',  # Silver version
            'title': 'Johto',
            'description': 'Generation II expanded the Pokemon world with Gold and Silver versions.'
        },
        3: {
            'css_file': 'themes/gen3.css',
            'primary_color': '#a00000',  # Ruby version
            'secondary_color': '#0000a0',  # Sapphire version
            'title': 'Hoenn',
            'description': 'Generation III brought us to the tropical Hoenn region with Ruby and Sapphire versions.'
        },
        4: {
            'css_file': 'base.css',  # Default theme for now
            'primary_color': '#aaaaff',  # Diamond version
            'secondary_color': '#ffaaaa',  # Pearl version
            'title': 'Sinnoh',
            'description': 'Generation IV featured the Sinnoh region in Diamond and Pearl versions.'
        },
        5: {
            'css_file': 'base.css',  # Default theme for now
            'primary_color': '#000000',  # Black version
            'secondary_color': '#ffffff',  # White version
            'title': 'Unova',
            'description': 'Generation V took place in the Unova region with Black and White versions.'
        },
        6: {
            'css_file': 'base.css',  # Default theme for now
            'primary_color': '#ff0000',  # X version
            'secondary_color': '#0000ff',  # Y version
            'title': 'Kalos',
            'description': 'Generation VI introduced the Kalos region in Pokemon X and Y.'
        },
        7: {
            'css_file': 'base.css',  # Default theme for now
            'primary_color': '#ff9900',  # Sun version
            'secondary_color': '#9999ff',  # Moon version
            'title': 'Alola',
            'description': 'Generation VII featured the tropical Alola region in Sun and Moon versions.'
        },
        8: {
            'css_file': 'base.css',  # Default theme for now
            'primary_color': '#3075b0',  # Sword version
            'secondary_color': '#8f4c96',  # Shield version
            'title': 'Galar',
            'description': 'Generation VIII brought us to the Galar region with Sword and Shield versions.'
        },
        9: {
            'css_file': 'base.css',  # Default theme for now
            'primary_color': '#ab2813',  # Scarlet version
            'secondary_color': '#5e65ae',  # Violet version
            'title': 'Paldea',
            'description': 'Generation IX takes place in the Paldea region with Scarlet and Violet versions.'
        }
    }
    
    # Default to first generation if the requested generation is not available
    return themes.get(generation, themes[1]) 