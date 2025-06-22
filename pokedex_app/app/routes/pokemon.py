from flask import Blueprint, render_template, abort, request, redirect, url_for
from pokedex_app.app.models.mongodb import mongo
from pokedex_app.app.services.theme_service import get_generation_theme
from pokedex_app.app.utils.helpers import calculate_type_effectiveness, get_pokemon_moves, get_pokemon_abilities

pokemon_bp = Blueprint('pokemon', __name__, url_prefix='/pokemon')

@pokemon_bp.route('/')
def pokemon_list():
    page = int(request.args.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page
    
    # Get filters
    generation = request.args.get('generation')
    type_filter = request.args.get('type')
    query = request.args.get('q', '')
    
    # Build MongoDB query
    mongo_query = {}
    
    if generation:
        try:
            mongo_query['generation'] = int(generation)
        except ValueError:
            pass
    
    if type_filter:
        mongo_query['type'] = type_filter
    
    if query:
        mongo_query['$or'] = [
            {'name.english': {'$regex': query, '$options': 'i'}},
            {'id': {'$eq': int(query)}} if query.isdigit() else {'name.english': {'$regex': query, '$options': 'i'}}
        ]
    
    # Get Pokémon data
    total = mongo.get_collection('pokemon').count_documents(mongo_query)
    pokemon_list = list(mongo.get_collection('pokemon')
                       .find(mongo_query)
                       .sort('id', 1)
                       .skip(skip)
                       .limit(per_page))
    
    # Get all types for filtering
    types = list(mongo.get_collection('types').find({}, {'english': 1, 'color': 1}))
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('pokemon/list.html',
                          pokemon_list=pokemon_list,
                          types=types,
                          current_page=page,
                          total_pages=total_pages,
                          generation=generation,
                          type_filter=type_filter,
                          query=query)

@pokemon_bp.route('/<int:pokedex_id>')
def pokemon_detail(pokedex_id):
    pokemon = mongo.get_collection('pokemon').find_one({'id': pokedex_id})
    
    if not pokemon:
        abort(404)
    
    # Get generation theme
    theme = get_generation_theme(pokemon.get('generation', 1))
    
    # Get evolution chain
    evolution_chain = []
    
    # If Pokémon has previous evolution
    if pokemon.get('evolution') and 'prev' in pokemon['evolution']:
        prev_id = int(pokemon['evolution']['prev'][0])
        prev_pokemon = mongo.get_collection('pokemon').find_one({'id': prev_id})
        if prev_pokemon:
            evolution_chain.append({
                'id': prev_pokemon['id'],
                'name': prev_pokemon['name']['english'],
                'image': {
                    'sprite': prev_pokemon['image']['sprite'],
                    'thumbnail': prev_pokemon['image']['thumbnail'],
                    'hires': prev_pokemon['image']['hires']
                },
                'evolution_level': pokemon['evolution']['prev'][1] if len(pokemon['evolution']['prev']) > 1 else None,
                'evolution_details': pokemon['evolution']['prev'][1] if len(pokemon['evolution']['prev']) > 1 else None
            })
    
    # Add current Pokémon
    evolution_chain.append({
        'id': pokemon['id'],
        'name': pokemon['name']['english'],
        'image': {
            'sprite': pokemon['image']['sprite'],
            'thumbnail': pokemon['image']['thumbnail'],
            'hires': pokemon['image']['hires']
        },
        'evolution_level': None,
        'evolution_details': None
    })
    
    # If Pokémon has next evolutions
    if pokemon.get('evolution') and 'next' in pokemon['evolution']:
        for next_evo in pokemon['evolution']['next']:
            next_id = int(next_evo[0])
            next_pokemon = mongo.get_collection('pokemon').find_one({'id': next_id})
            if next_pokemon:
                evolution_chain.append({
                    'id': next_pokemon['id'],
                    'name': next_pokemon['name']['english'],
                    'image': {
                        'sprite': next_pokemon['image']['sprite'],
                        'thumbnail': next_pokemon['image']['thumbnail'],
                        'hires': next_pokemon['image']['hires']
                    },
                    'evolution_level': next_evo[1] if len(next_evo) > 1 else None,
                    'evolution_details': next_evo[1] if len(next_evo) > 1 else None
                })
    
    # Get type effectiveness
    type_effectiveness = calculate_type_effectiveness(pokemon['type'])
    
    # Get moves for this Pokémon
    move_categories = get_pokemon_moves(pokedex_id)
    
    # Flatten moves list for the template
    moves = []
    for category, category_moves in move_categories.items():
        moves.extend(category_moves)
    
    # Get abilities for this Pokémon
    abilities = get_pokemon_abilities(pokedex_id)
    
    # Make sure we have the 'stats' field as expected in the template
    if 'stats' not in pokemon:
        # Try to build from 'base' if available
        base = pokemon.get('base', {})
        pokemon['stats'] = {
            'hp': base.get('HP', 0),
            'attack': base.get('Attack', 0),
            'defense': base.get('Defense', 0),
            'special_attack': base.get('Sp. Attack', 0),
            'special_defense': base.get('Sp. Defense', 0),
            'speed': base.get('Speed', 0),
        }
    # If stats exist but use uppercase keys, normalize them
    elif 'HP' in pokemon['stats']:
        s = pokemon['stats']
        pokemon['stats'] = {
            'hp': s.get('HP', 0),
            'attack': s.get('Attack', 0),
            'defense': s.get('Defense', 0),
            'special_attack': s.get('Sp. Attack', 0),
            'special_defense': s.get('Sp. Defense', 0),
            'speed': s.get('Speed', 0),
        }
    
    return render_template('pokemon/detail.html',
                          pokemon=pokemon,
                          evolution_chain=evolution_chain,
                          type_effectiveness=type_effectiveness,
                          moves=moves,
                          abilities=abilities,
                          theme=theme)

@pokemon_bp.route('/compare')
def compare():
    pokemon_ids = request.args.getlist('ids')
    
    if not pokemon_ids or len(pokemon_ids) != 2:
        return render_template('pokemon/compare.html', pokemon1=None, pokemon2=None)
    
    try:
        pokemon1_id = int(pokemon_ids[0])
        pokemon2_id = int(pokemon_ids[1])
        
        pokemon1 = mongo.get_collection('pokemon').find_one({'id': pokemon1_id})
        pokemon2 = mongo.get_collection('pokemon').find_one({'id': pokemon2_id})
        
        if pokemon1 and pokemon2:
            # Add type effectiveness for both Pokemon
            pokemon1['type_effectiveness'] = calculate_type_effectiveness(pokemon1['types'])
            pokemon2['type_effectiveness'] = calculate_type_effectiveness(pokemon2['types'])
            
            # Calculate stats total for both
            pokemon1['stats']['total'] = sum(stat for stat in pokemon1['stats'].values() if isinstance(stat, int))
            pokemon2['stats']['total'] = sum(stat for stat in pokemon2['stats'].values() if isinstance(stat, int))
            
            return render_template('pokemon/compare.html', 
                pokemon1=pokemon1, 
                pokemon2=pokemon2)
        
    except (ValueError, IndexError):
        pass
    
    return render_template('pokemon/compare.html', pokemon1=None, pokemon2=None)

@pokemon_bp.route('/items')
def items_list():
    page = int(request.args.get('page', 1))
    per_page = 24
    skip = (page - 1) * per_page
    
    # Get filters
    category = request.args.get('category')
    query = request.args.get('q', '')
    
    # Build MongoDB query
    mongo_query = {}
    
    if category:
        mongo_query['category'] = category
    
    if query:
        mongo_query['name'] = {'$regex': query, '$options': 'i'}
    
    # Get items data
    total = mongo.get_collection('items').count_documents(mongo_query)
    items_list = list(mongo.get_collection('items')
                    .find(mongo_query)
                    .sort('id', 1)
                    .skip(skip)
                    .limit(per_page))
    
    # Get item categories for filtering
    categories = mongo.get_collection('items').distinct('category')
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('pokemon/items.html',
                          items_list=items_list,
                          categories=categories,
                          current_page=page,
                          total_pages=total_pages,
                          category=category,
                          query=query)

@pokemon_bp.route('/moves')
def moves_list():
    page = int(request.args.get('page', 1))
    per_page = 30
    skip = (page - 1) * per_page
    
    # Get filters
    move_type = request.args.get('type')
    category = request.args.get('category')
    query = request.args.get('q', '')
    
    # Build MongoDB query
    mongo_query = {}
    
    if move_type:
        mongo_query['type'] = move_type
        
    # For now, we can't filter by category as it's in Japanese
    # when we have proper mapping we can uncomment this
    # if category:
    #    mongo_query['category'] = category
    
    if query:
        mongo_query['ename'] = {'$regex': query, '$options': 'i'}
    
    # Get moves data
    total = mongo.get_collection('moves').count_documents(mongo_query)
    moves_data = list(mongo.get_collection('moves')
                    .find(mongo_query)
                    .sort('id', 1)
                    .skip(skip)
                    .limit(per_page))
    
    # Map category names to English
    category_map = {
        "物理": "physical",
        "特殊": "special", 
        "变化": "status"
    }
    
    # Transform moves data to match template expectations
    moves_list = []
    for move in moves_data:
        # Map the Japanese category to English or use "status" as default
        eng_category = category_map.get(move.get('category', ''), 'status')
        
        # Create properly structured move data
        formatted_move = {
            'name': move.get('ename', 'Unknown'),
            'type': move.get('type', 'Normal'),
            'category': eng_category,
            'power': move.get('power', 0),
            'accuracy': move.get('accuracy', 0),
            'pp': move.get('pp', 0),
            'effect': move.get('effect', 'No effect information available.')
        }
        moves_list.append(formatted_move)
    
    # Get all types for filtering
    types = list(mongo.get_collection('types').find({}, {'english': 1, 'color': 1}))
    
    # Get categories
    categories = ['physical', 'special', 'status']
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('pokemon/moves.html',
                          moves_list=moves_list,
                          types=types,
                          categories=categories,
                          current_page=page,
                          total_pages=total_pages,
                          move_type=move_type,
                          category=category,
                          query=query)

@pokemon_bp.route('/team-builder')
def team_builder():
    # Get all types for type coverage analysis
    types = list(mongo.get_collection('types').find({}, {'name': 1, 'color': 1, 'weaknesses': 1, 'strengths': 1}))
    
    return render_template('pokemon/team_builder.html', types=types) 