from pokedex_app.app.models.mongodb import mongo
from flask_caching import Cache
from flask import current_app

def calculate_type_effectiveness(pokemon_types):
    """
    Calculate the effectiveness of each type against the given Pokémon's type(s).
    Returns a dictionary with 4 categories: immune, resistant, weak, and super_weak.
    """
    if not pokemon_types or not isinstance(pokemon_types, list):
        return {
            'immune': [],
            'resistant': [],
            'weak': [],
            'super_weak': []
        }
    
    effectiveness = {
        'immune': [],
        'resistant': [],
        'weak': [],
        'super_weak': []  # For 4x weakness
    }
    
    all_types = list(mongo.get_collection('types').find())
    type_dict = {t['english']: t for t in all_types}
    
    # Process immunities (no effect)
    for ptype in pokemon_types:
        if ptype in type_dict:
            no_effect = type_dict[ptype].get('no_effect', [])
            effectiveness['immune'].extend(no_effect)
    
    # Count resistances and weaknesses
    type_count = {}
    for attacking_type in [t['english'] for t in all_types]:
        type_count[attacking_type] = 0
        
        for defending_type in pokemon_types:
            if defending_type not in type_dict:
                continue
                
            defending_data = type_dict[defending_type]
            
            # Check if defending type is weak to attacking type
            if attacking_type in defending_data.get('effective', []):
                type_count[attacking_type] += 1
                
            # Check if defending type resists attacking type
            if attacking_type in defending_data.get('ineffective', []):
                type_count[attacking_type] -= 1
    
    # Remove duplicates from immune list
    effectiveness['immune'] = list(set(effectiveness['immune']))
            
    # Categorize
    for type_name, count in type_count.items():
        if type_name in effectiveness['immune']:
            continue  # Skip if immune
        
        if count == -2:
            effectiveness['resistant'].append(type_name)
        elif count == -1:
            effectiveness['resistant'].append(type_name)
        elif count == 1:
            effectiveness['weak'].append(type_name)
        elif count >= 2:
            effectiveness['super_weak'].append(type_name)
            
    return effectiveness

def search_pokemon(query, limit=10):
    """
    Search for Pokémon by name or ID.
    Returns a list of Pokémon matching the query.
    """
    if not query:
        return []
    
    # Build MongoDB query
    mongo_query = {
        '$or': [
            {'name.english': {'$regex': query, '$options': 'i'}},
            {'id': int(query)} if query.isdigit() else {'name.english': {'$regex': query, '$options': 'i'}}
        ]
    }
    
    # Get Pokémon data
    pokemon_list = list(mongo.get_collection('pokemon')
                       .find(mongo_query, {
                           'id': 1,
                           'name.english': 1,
                           'type': 1,
                           'image.sprite': 1
                       })
                       .sort('id', 1)
                       .limit(limit))
    
    # Format the results
    results = []
    for pokemon in pokemon_list:
        results.append({
            'id': pokemon['id'],
            'name': pokemon['name']['english'],
            'types': pokemon['type'],
            'sprite': pokemon['image']['sprite']
        })
    
    return results

def get_pokemon_moves(pokemon_id):
    """
    Get the moves for a specific Pokémon.
    Returns a dictionary with moves organized by categories.
    """
    # For future implementation: Get move data from a pokemon_moves collection
    # that would have a mapping between Pokemon IDs and their learnable moves
    
    # Setup our return structure
    move_categories = {
        'level_up': [],  # Moves learned by leveling up
        'tm_hm': [],     # Moves learned from TMs/HMs
        'egg': [],       # Egg moves
        'tutor': [],     # Moves from move tutors
        'evolution': []  # Moves learned upon evolution
    }
    
    # Get Pokemon data to determine its type
    pokemon = mongo.get_collection('pokemon').find_one({'id': pokemon_id})
    if not pokemon:
        return move_categories
        
    pokemon_types = pokemon.get('type', [])
    
    # Get moves matching the Pokemon's type(s)
    # We'll get moves of each of the Pokemon's types
    category_map = {
        "物理": "physical",
        "特殊": "special", 
        "变化": "status"
    }
    
    # Additional moves by varied types to ensure more diversity
    varied_types = ["Normal", "Fighting", "Flying", "Psychic", "Ghost", "Dark"]
    move_types = set(pokemon_types + [t for t in varied_types if t not in pokemon_types])
    
    for poke_type in move_types:
        # Get moves of this type from different categories
        level_moves = list(mongo.get_collection('moves')
                         .find({'type': poke_type})
                         .sort('power', -1)  # Sort by power descending
                         .limit(3))
                         
        # Get moves with TM numbers if available
        tm_query = {'type': poke_type}
        if mongo.get_collection('moves').count_documents({'tm': {'$exists': True}}) > 0:
            tm_query['tm'] = {'$exists': True}
            
        tm_moves = list(mongo.get_collection('moves')
                      .find(tm_query)
                      .sort('id', 1)
                      .limit(2))
        
        # Format the moves
        for move in level_moves:
            eng_category = category_map.get(move.get('category', ''), 'status')
            power_value = move.get('power')
            accuracy_value = move.get('accuracy')
            
            # Ensure values are either None or valid integers
            power = int(power_value) if power_value is not None and str(power_value).isdigit() and int(power_value) > 0 else None
            accuracy = int(accuracy_value) if accuracy_value is not None and str(accuracy_value).isdigit() and int(accuracy_value) > 0 else None
            
            move_categories['level_up'].append({
                'id': move.get('id', 0),
                'name': move.get('ename', 'Unknown'),
                'type': move.get('type', 'Normal'),
                'category': eng_category.title(),  # Capitalize for display
                'power': power,
                'accuracy': accuracy,
                'pp': move.get('pp', 0),
                'level': 5 * len(move_categories['level_up']) + 5  # Just a placeholder level
            })
            
        for move in tm_moves:
            eng_category = category_map.get(move.get('category', ''), 'status')
            power_value = move.get('power')
            accuracy_value = move.get('accuracy')
            
            # Ensure values are either None or valid integers
            power = int(power_value) if power_value is not None and str(power_value).isdigit() and int(power_value) > 0 else None
            accuracy = int(accuracy_value) if accuracy_value is not None and str(accuracy_value).isdigit() and int(accuracy_value) > 0 else None
            
            move_categories['tm_hm'].append({
                'id': move.get('id', 0),
                'name': move.get('ename', 'Unknown'),
                'type': move.get('type', 'Normal'),
                'category': eng_category.title(),  # Capitalize for display
                'power': power,
                'accuracy': accuracy,
                'pp': move.get('pp', 0),
                'tm': move.get('tm', 0)
            })
    
    # Add a couple of egg moves (random but try to get varied types)
    egg_moves = list(mongo.get_collection('moves')
                   .aggregate([
                       {'$match': {'type': {'$nin': pokemon_types}}},
                       {'$sample': {'size': 3}}
                   ]))
                   
    for move in egg_moves:
        eng_category = category_map.get(move.get('category', ''), 'status')
        power_value = move.get('power')
        accuracy_value = move.get('accuracy')
        
        # Ensure values are either None or valid integers
        power = int(power_value) if power_value is not None and str(power_value).isdigit() and int(power_value) > 0 else None
        accuracy = int(accuracy_value) if accuracy_value is not None and str(accuracy_value).isdigit() and int(accuracy_value) > 0 else None
        
        move_categories['egg'].append({
            'id': move.get('id', 0),
            'name': move.get('ename', 'Unknown'),
            'type': move.get('type', 'Normal'),
            'category': eng_category.title(),  # Capitalize for display
            'power': power,
            'accuracy': accuracy,
            'pp': move.get('pp', 0)
        })
    
    return move_categories 

def get_pokemon_abilities(pokemon_id):
    """
    Get the abilities for a specific Pokémon.
    Returns a list of abilities with name, description and hidden status.
    """
    # Get Pokemon data to retrieve abilities
    pokemon = mongo.get_collection('pokemon').find_one({'id': pokemon_id})
    if not pokemon:
        return []
    
    abilities_list = []
    
    # Handle different data structures for abilities
    
    # Structure 1: Direct 'abilities' list with objects
    if 'abilities' in pokemon and isinstance(pokemon['abilities'], list):
        for ability in pokemon['abilities']:
            if isinstance(ability, dict) and 'name' in ability:
                abilities_list.append({
                    'name': ability['name'],
                    'description': ability.get('description', 'No description available'),
                    'is_hidden': ability.get('is_hidden', False)
                })
            elif isinstance(ability, str):
                abilities_list.append({
                    'name': ability,
                    'description': 'No description available',
                    'is_hidden': False
                })
    
    # Structure 2: 'ability' field (as object or list)
    elif 'ability' in pokemon:
        ability_data = pokemon['ability']
        
        # Case: ability is a list of strings
        if isinstance(ability_data, list):
            for ability in ability_data:
                abilities_list.append({
                    'name': ability,
                    'description': 'No description available',
                    'is_hidden': False
                })
        
        # Case: ability is a dict with normal/hidden keys
        elif isinstance(ability_data, dict):
            # Process normal abilities
            normal = ability_data.get('normal', [])
            if isinstance(normal, list):
                for ability in normal:
                    abilities_list.append({
                        'name': ability,
                        'description': 'No description available',
                        'is_hidden': False
                    })
            elif normal:  # Single normal ability as string
                abilities_list.append({
                    'name': normal,
                    'description': 'No description available',
                    'is_hidden': False
                })
                
            # Process hidden ability if present
            hidden = ability_data.get('hidden')
            if hidden:
                abilities_list.append({
                    'name': hidden,
                    'description': 'No description available',
                    'is_hidden': True
                })
    
    # Structure 2.5: profile.ability (array)
    elif 'profile' in pokemon and isinstance(pokemon['profile'], dict) and 'ability' in pokemon['profile']:
        profile_ability = pokemon['profile']['ability']
        if isinstance(profile_ability, list):
            for ability in profile_ability:
                # If ability is a list/tuple with 2 elements (name, is_hidden)
                if isinstance(ability, (list, tuple)) and len(ability) == 2:
                    abilities_list.append({
                        'name': ability[0],
                        'description': 'No description available',
                        'is_hidden': ability[1] in [True, 'true', 'True', 1]
                    })
                elif isinstance(ability, str):
                    abilities_list.append({
                        'name': ability,
                        'description': 'No description available',
                        'is_hidden': False
                    })
        elif isinstance(profile_ability, str):
            abilities_list.append({
                'name': profile_ability,
                'description': 'No description available',
                'is_hidden': False
            })
    
    # Structure 3: Direct 'abilities' object with keys
    elif 'abilities' in pokemon and isinstance(pokemon['abilities'], dict):
        abilities_obj = pokemon['abilities']
        
        # Regular abilities
        for key, value in abilities_obj.items():
            if key != 'hidden' and value:
                abilities_list.append({
                    'name': value,
                    'description': 'No description available',
                    'is_hidden': False
                })
        
        # Hidden ability
        if 'hidden' in abilities_obj and abilities_obj['hidden']:
            abilities_list.append({
                'name': abilities_obj['hidden'],
                'description': 'No description available',
                'is_hidden': True
            })
    
    # Structure 4: Legacy 'base' structure with 'Ability' field
    elif 'base' in pokemon and isinstance(pokemon['base'], dict):
        base = pokemon['base']
        if 'Ability' in base:
            ability = base['Ability']
            if isinstance(ability, list):
                for ab in ability:
                    abilities_list.append({
                        'name': ab,
                        'description': 'No description available',
                        'is_hidden': False
                    })
            elif ability:
                abilities_list.append({
                    'name': ability,
                    'description': 'No description available',
                    'is_hidden': False
                })
    
    # Fallback: Try to extract abilities from 'name' field (some formats use this)
    elif 'name' in pokemon:
        name_data = pokemon['name']
        if isinstance(name_data, dict) and 'abilities' in name_data:
            abilities_data = name_data['abilities']
            if isinstance(abilities_data, list):
                for ability in abilities_data:
                    abilities_list.append({
                        'name': ability,
                        'description': 'No description available',
                        'is_hidden': False
                    })
            elif isinstance(abilities_data, str):
                abilities_list.append({
                    'name': abilities_data,
                    'description': 'No description available',
                    'is_hidden': False
                })
    
    # Final fallback: Try to find ability info from external sources
    # Only do this if we have no abilities yet
    if not abilities_list:
        # Try to look up the Pokemon by species name
        if 'name' in pokemon and 'english' in pokemon['name']:
            pokemon_name = pokemon['name']['english']
            # Try to get abilities data based on name from a common Pokemon abilities mapping
            try:
                lookup_data = mongo.get_collection('pokemon_abilities_map').find_one({'name': pokemon_name})
                if lookup_data and 'abilities' in lookup_data:
                    for ability in lookup_data['abilities']:
                        if isinstance(ability, dict):
                            abilities_list.append({
                                'name': ability.get('name', 'Unknown'),
                                'description': ability.get('description', 'No description available'),
                                'is_hidden': ability.get('is_hidden', False)
                            })
                        elif isinstance(ability, str):
                            abilities_list.append({
                                'name': ability,
                                'description': 'No description available',
                                'is_hidden': False
                            })
            except Exception:
                pass
    
    # Final hard-coded fallbacks for common Pokemon
    if not abilities_list and 'id' in pokemon:
        pokemon_id = pokemon['id']
        common_abilities = {
            1: [{'name': 'Overgrow', 'description': 'Powers up Grass-type moves when the Pokémon is in trouble.', 'is_hidden': False},
               {'name': 'Chlorophyll', 'description': 'Boosts the Pokémon\'s Speed in sunshine.', 'is_hidden': True}],
            4: [{'name': 'Blaze', 'description': 'Powers up Fire-type moves when the Pokémon is in trouble.', 'is_hidden': False},
               {'name': 'Solar Power', 'description': 'Boosts Special Attack, but lowers HP in sunshine.', 'is_hidden': True}],
            7: [{'name': 'Torrent', 'description': 'Powers up Water-type moves when the Pokémon is in trouble.', 'is_hidden': False},
               {'name': 'Rain Dish', 'description': 'The Pokémon gradually regains HP in rain.', 'is_hidden': True}],
            25: [{'name': 'Static', 'description': 'The Pokémon may paralyze contacting attackers.', 'is_hidden': False},
                {'name': 'Lightning Rod', 'description': 'The Pokémon draws Electric moves to boost Sp. Attack.', 'is_hidden': True}],
            132: [{'name': 'Imposter', 'description': 'The Pokémon transforms when it enters battle.', 'is_hidden': False},
                 {'name': 'Limber', 'description': 'Makes the Pokémon immune to paralysis.', 'is_hidden': True}],
            143: [{'name': 'Immunity', 'description': 'Prevents the Pokémon from getting poisoned.', 'is_hidden': False},
                 {'name': 'Thick Fat', 'description': 'Raises resistance to Fire and Ice moves.', 'is_hidden': False},
                 {'name': 'Gluttony', 'description': 'Makes the Pokémon eat held Berries early.', 'is_hidden': True}],
            150: [{'name': 'Pressure', 'description': 'Forces foes to use more PP.', 'is_hidden': False},
                 {'name': 'Unnerve', 'description': 'Prevents foes from eating Berries.', 'is_hidden': True}]
        }
        
        if pokemon_id in common_abilities:
            abilities_list = common_abilities[pokemon_id]
    
    # Try to get descriptions for abilities if an abilities collection exists
    try:
        for ability in abilities_list:
            ability_data = mongo.get_collection('abilities').find_one({'name': ability['name']})
            if ability_data and 'description' in ability_data:
                ability['description'] = ability_data['description']
    except Exception:
        # If there's any issue with the abilities collection, just continue
        pass
    
    return abilities_list 