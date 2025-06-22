from flask import Blueprint, render_template, request, jsonify, session
from pokedex_app.app.models.mongodb import mongo
from pokedex_app.app.services.pokemon_service import get_pokemon_by_id
from bson.objectid import ObjectId

# Create a Blueprint for team builder routes
team_builder_bp = Blueprint('team_builder', __name__, url_prefix='/team-builder')

@team_builder_bp.route('/', methods=['GET'])
def team_builder():
    """Render the team builder page."""
    # Get team from session if it exists, otherwise create empty team
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    # Get all Pokemon for the selector
    pokemon_collection = mongo.get_collection('pokemon')
    all_pokemon = list(pokemon_collection.find({}, 
                                             {'id': 1, 'name': 1, 'type': 1, 'image.sprite': 1})
                      .sort('id', 1))
    
    return render_template('team_builder/index.html', team=team, all_pokemon=all_pokemon)

@team_builder_bp.route('/add', methods=['POST'])
def add_pokemon():
    """Add a Pokemon to the team."""
    data = request.json
    pokemon_id = int(data.get('pokemon_id'))
    
    # Get the team from session or create a new one
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    # Check if team is already full (6 Pokemon)
    if len(team['pokemon']) >= 6:
        return jsonify({'success': False, 'message': 'Team is already full (max 6 Pokemon)'}), 400
    
    # Get Pokemon data
    pokemon = get_pokemon_by_id(pokemon_id)
    if not pokemon:
        return jsonify({'success': False, 'message': 'Pokemon not found'}), 404
    
    # Add Pokemon to team
    team_member = {
        'pokemon': pokemon,
        'moves': [],
        'ability': None,
        'item': None,
        'position': len(team['pokemon'])
    }
    
    team['pokemon'].append(team_member)
    session['team'] = team
    
    return jsonify({'success': True, 'team': team})

@team_builder_bp.route('/remove/<int:position>', methods=['DELETE'])
def remove_pokemon(position):
    """Remove a Pokemon from the team."""
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    if 0 <= position < len(team['pokemon']):
        # Remove Pokemon at the specified position
        team['pokemon'].pop(position)
        
        # Reindex positions
        for i, member in enumerate(team['pokemon']):
            member['position'] = i
        
        session['team'] = team
        return jsonify({'success': True, 'team': team})
    
    return jsonify({'success': False, 'message': 'Invalid position'}), 400

@team_builder_bp.route('/clear', methods=['POST'])
def clear_team():
    """Clear the entire team."""
    team_name = session.get('team', {}).get('name', 'My Team')
    session['team'] = {'pokemon': [], 'name': team_name}
    return jsonify({'success': True, 'team': session['team']})

@team_builder_bp.route('/update/<int:position>', methods=['POST'])
def update_team_member(position):
    """Update a team member's moves, ability or item."""
    data = request.json
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    if 0 <= position < len(team['pokemon']):
        # Update the specified fields
        if 'moves' in data:
            team['pokemon'][position]['moves'] = data['moves']
        if 'ability' in data:
            team['pokemon'][position]['ability'] = data['ability']
        if 'item' in data:
            team['pokemon'][position]['item'] = data['item']
        
        session['team'] = team
        return jsonify({'success': True, 'team': team})
    
    return jsonify({'success': False, 'message': 'Invalid position'}), 400

@team_builder_bp.route('/rename', methods=['POST'])
def rename_team():
    """Rename the team."""
    data = request.json
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    team['name'] = data.get('name', 'My Team')
    session['team'] = team
    
    return jsonify({'success': True, 'team': team})

@team_builder_bp.route('/analyze', methods=['GET'])
def analyze_team():
    """Analyze the current team's strengths and weaknesses."""
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    # Initialize type effectiveness counter
    type_effectiveness = {
        'weaknesses': {},
        'resistances': {},
        'immunities': {}
    }
    
    # Get all type data
    types_collection = mongo.get_collection('types')
    types = {t['name']: t for t in types_collection.find()}
    
    # Analyze each Pokemon in the team
    for member in team['pokemon']:
        pokemon = member['pokemon']
        pokemon_types = pokemon['type']
        
        # Process each Pokemon's type effectiveness
        for attack_type, type_data in types.items():
            # Skip if this is one of the Pokemon's types
            damage_factor = 1.0
            
            # Calculate damage factor based on Pokemon's types
            for poke_type in pokemon_types:
                if attack_type in types[poke_type]['immunes']:
                    damage_factor = 0
                    break
                elif attack_type in types[poke_type]['weaknesses']:
                    damage_factor *= 2
                elif attack_type in types[poke_type]['resistances']:
                    damage_factor *= 0.5
            
            # Register the effectiveness
            if damage_factor > 1:
                type_effectiveness['weaknesses'][attack_type] = type_effectiveness['weaknesses'].get(attack_type, 0) + 1
            elif damage_factor < 1 and damage_factor > 0:
                type_effectiveness['resistances'][attack_type] = type_effectiveness['resistances'].get(attack_type, 0) + 1
            elif damage_factor == 0:
                type_effectiveness['immunities'][attack_type] = type_effectiveness['immunities'].get(attack_type, 0) + 1
    
    # Sort effectiveness by count
    for category in type_effectiveness:
        type_effectiveness[category] = dict(sorted(
            type_effectiveness[category].items(),
            key=lambda item: item[1],
            reverse=True
        ))
    
    return jsonify({
        'success': True, 
        'analysis': type_effectiveness, 
        'team': team
    })

@team_builder_bp.route('/save', methods=['POST'])
def save_team():
    """Save team to database for the user."""
    # In a real app, you'd associate this with a user
    # For this demo, we'll just save it to the database
    team = session.get('team', {'pokemon': [], 'name': 'My Team'})
    
    if not team['pokemon']:
        return jsonify({'success': False, 'message': 'Cannot save empty team'}), 400
    
    # Save to database
    teams_collection = mongo.get_collection('teams')
    result = teams_collection.insert_one(team)
    
    return jsonify({
        'success': True, 
        'message': 'Team saved successfully',
        'team_id': str(result.inserted_id)
    })

@team_builder_bp.route('/list', methods=['GET'])
def list_teams():
    """List all saved teams."""
    teams_collection = mongo.get_collection('teams')
    teams = list(teams_collection.find())
    
    # Convert ObjectId to string
    for team in teams:
        team['_id'] = str(team['_id'])
    
    return jsonify({'success': True, 'teams': teams})

@team_builder_bp.route('/load/<team_id>', methods=['GET'])
def load_team(team_id):
    """Load a team from the database."""
    teams_collection = mongo.get_collection('teams')
    
    try:
        team = teams_collection.find_one({'_id': ObjectId(team_id)})
        if team:
            # Remove the ObjectId
            team['_id'] = str(team['_id'])
            # Save to session
            session['team'] = team
            return jsonify({'success': True, 'team': team})
        else:
            return jsonify({'success': False, 'message': 'Team not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400 