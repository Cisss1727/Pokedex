from flask import Blueprint, request, jsonify
from pokedex_app.app.models.mongodb import mongo
from pokedex_app.app.utils.helpers import search_pokemon

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/')
def search():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Get search results
    results = search_pokemon(query, limit)
    
    return jsonify(results) 