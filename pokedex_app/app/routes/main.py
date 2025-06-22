from flask import Blueprint, render_template
from pokedex_app.app.models.mongodb import mongo

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get a few Pokémon from each generation
    pokemon_by_gen = {}
    
    for gen in range(1, 10):  # Generations 1-9
        pokemon = list(mongo.get_collection('pokemon')
                      .find({'generation': gen})
                      .sort('id', 1)  # Sort by proper ID field
                      .limit(8))  # 8 Pokémon per generation
        
        if pokemon:  # If we have Pokémon for this generation
            pokemon_by_gen[gen] = pokemon
    
    return render_template('index.html', pokemon_by_gen=pokemon_by_gen) 