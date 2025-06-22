from flask import Blueprint, jsonify, request, render_template
from pokedex_app.app.models.mongodb import mongo
from pokedex_app.app.utils.helpers import calculate_type_effectiveness
from pokedex_app.app.services.theme_service import get_generation_theme
from flask_caching import Cache
from bson import json_util
import json

api_bp = Blueprint('api', __name__)

# Helper function to convert MongoDB BSON to JSON
def parse_json(data):
    return json.loads(json_util.dumps(data))

@api_bp.route('/pokemon')
def get_pokemon_list():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('limit', 20))
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
            {'id': int(query)} if query.isdigit() else {'name.english': {'$regex': query, '$options': 'i'}}
        ]
    
    # Get Pokémon data
    total = mongo.get_collection('pokemon').count_documents(mongo_query)
    pokemon_list = list(mongo.get_collection('pokemon')
                       .find(mongo_query)
                       .sort('id', 1)
                       .skip(skip)
                       .limit(per_page))
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'pokemon': parse_json(pokemon_list),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }
    })

@api_bp.route('/pokemon/<int:pokemon_id>')
def get_pokemon(pokemon_id):
    pokemon = mongo.get_collection('pokemon').find_one({'id': pokemon_id})
    
    if not pokemon:
        return jsonify({'error': 'Pokemon not found'}), 404
    
    # Get type effectiveness
    type_effectiveness = calculate_type_effectiveness(pokemon['type'])
    
    # Add type effectiveness to response
    pokemon_data = parse_json(pokemon)
    pokemon_data['type_effectiveness'] = type_effectiveness
    
    return jsonify(pokemon_data)

@api_bp.route('/types')
def get_types():
    types = list(mongo.get_collection('types').find())
    return jsonify(parse_json(types))

@api_bp.route('/moves')
def get_moves():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('limit', 50))
    skip = (page - 1) * per_page
    
    # Get filters
    type_filter = request.args.get('type')
    query = request.args.get('q', '')
    
    # Build MongoDB query
    mongo_query = {}
    
    if type_filter:
        mongo_query['type'] = type_filter
    
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
    
    # Transform moves data
    formatted_moves = []
    for move in moves_data:
        # Map the Japanese category to English
        eng_category = category_map.get(move.get('category', ''), 'status')
        
        # Create properly structured move data
        formatted_move = {
            'id': move.get('id', 0),
            'name': move.get('ename', 'Unknown'),
            'type': move.get('type', 'Normal'),
            'category': eng_category,
            'power': move.get('power', None),
            'accuracy': move.get('accuracy', None),
            'pp': move.get('pp', 0),
        }
        formatted_moves.append(formatted_move)
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'moves': formatted_moves,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }
    })

@api_bp.route('/generations/<int:gen_number>/theme')
def get_theme(gen_number):
    theme = get_generation_theme(gen_number)
    return jsonify(theme)

@api_bp.route('/docs', methods=['GET'])
def api_docs():
    """API documentation page."""
    return render_template('api/docs.html') 