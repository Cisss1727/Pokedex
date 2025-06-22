from pokedex_app.app.models.mongodb import mongo
from flask_caching import Cache
from flask import current_app
import os

# Initialize cache
cache = Cache()

@cache.memoize(timeout=3600)  # Cache for 1 hour
def get_pokemon_by_id(pokemon_id):
    """Get a Pokemon by its Pokedex ID."""
    pokemon_collection = mongo.get_collection('pokemon')
    pokemon = pokemon_collection.find_one({"id": pokemon_id})
    return pokemon

@cache.memoize(timeout=3600)
def get_pokemon_by_name(name):
    """Get a Pokemon by its name."""
    name = name.lower()
    pokemon_collection = mongo.get_collection('pokemon')
    
    # Try to match on english name
    pokemon = pokemon_collection.find_one({"name.english_lowercase": name})
    if pokemon:
        return pokemon
    
    # Try alternate names
    pokemon = pokemon_collection.find_one({
        "$or": [
            {"name.japanese_romanji_lowercase": name},
            {"name.chinese_lowercase": name},
            {"name.french_lowercase": name}
        ]
    })
    
    return pokemon

@cache.memoize(timeout=3600)
def get_pokemon_by_generation(generation, limit=None, skip=0):
    """Get all Pokemon from a specific generation."""
    pokemon_collection = mongo.get_collection('pokemon')
    query = {"generation": generation}
    
    # Apply limit if specified
    if limit:
        pokemon = list(pokemon_collection.find(query).sort("id", 1).skip(skip).limit(limit))
    else:
        pokemon = list(pokemon_collection.find(query).sort("id", 1).skip(skip))
    
    return pokemon

@cache.memoize(timeout=3600)
def get_pokemon_by_type(type_name, limit=None, skip=0):
    """Get all Pokemon of a specific type."""
    pokemon_collection = mongo.get_collection('pokemon')
    query = {"type": type_name}
    
    # Apply limit if specified
    if limit:
        pokemon = list(pokemon_collection.find(query).sort("id", 1).skip(skip).limit(limit))
    else:
        pokemon = list(pokemon_collection.find(query).sort("id", 1).skip(skip))
    
    return pokemon

@cache.memoize(timeout=3600)
def get_all_pokemon(limit=None, skip=0):
    """Get all Pokemon with optional pagination."""
    pokemon_collection = mongo.get_collection('pokemon')
    
    # Apply limit if specified
    if limit:
        pokemon = list(pokemon_collection.find().sort("id", 1).skip(skip).limit(limit))
    else:
        pokemon = list(pokemon_collection.find().sort("id", 1).skip(skip))
    
    return pokemon

@cache.memoize(timeout=3600)
def get_pokemon_count():
    """Get the total number of Pokemon in the database."""
    pokemon_collection = mongo.get_collection('pokemon')
    return pokemon_collection.count_documents({})

@cache.memoize(timeout=3600)
def get_pokemon_evolutions(pokemon_id):
    """Get evolution chain for a specific Pokemon."""
    pokemon_collection = mongo.get_collection('pokemon')
    pokemon = pokemon_collection.find_one({"id": pokemon_id})
    
    if not pokemon or "evolution" not in pokemon:
        return []
    
    evolution_chain = []
    
    # First get pre-evolutions
    if "prev" in pokemon["evolution"]:
        prev_id = pokemon["evolution"]["prev"][0]
        prev_pokemon = pokemon_collection.find_one({"id": prev_id})
        if prev_pokemon:
            # Check if there's an even earlier evolution
            if "evolution" in prev_pokemon and "prev" in prev_pokemon["evolution"]:
                first_id = prev_pokemon["evolution"]["prev"][0]
                first_pokemon = pokemon_collection.find_one({"id": first_id})
                if first_pokemon:
                    evolution_chain.append({
                        "id": first_pokemon["id"],
                        "name": first_pokemon["name"]["english"],
                        "image": first_pokemon["image"]["sprite"],
                        "stage": 1
                    })
            
            evolution_chain.append({
                "id": prev_pokemon["id"],
                "name": prev_pokemon["name"]["english"],
                "image": prev_pokemon["image"]["sprite"],
                "stage": len(evolution_chain) + 1
            })
    
    # Add the current Pokemon
    evolution_chain.append({
        "id": pokemon["id"],
        "name": pokemon["name"]["english"],
        "image": pokemon["image"]["sprite"],
        "stage": len(evolution_chain) + 1
    })
    
    # Then get next evolutions
    if "next" in pokemon["evolution"]:
        next_id = pokemon["evolution"]["next"][0]
        next_pokemon = pokemon_collection.find_one({"id": next_id})
        if next_pokemon:
            evolution_chain.append({
                "id": next_pokemon["id"],
                "name": next_pokemon["name"]["english"],
                "image": next_pokemon["image"]["sprite"],
                "stage": len(evolution_chain) + 1
            })
            
            # Check if there's a further evolution
            if "evolution" in next_pokemon and "next" in next_pokemon["evolution"]:
                final_id = next_pokemon["evolution"]["next"][0]
                final_pokemon = pokemon_collection.find_one({"id": final_id})
                if final_pokemon:
                    evolution_chain.append({
                        "id": final_pokemon["id"],
                        "name": final_pokemon["name"]["english"],
                        "image": final_pokemon["image"]["sprite"],
                        "stage": len(evolution_chain) + 1
                    })
    
    return evolution_chain

def search_pokemon(query, limit=20):
    """Search for Pokemon by name or ID."""
    query = query.lower().strip()
    pokemon_collection = mongo.get_collection('pokemon')
    
    results = []
    
    # Try to parse as ID
    try:
        pokemon_id = int(query)
        pokemon = pokemon_collection.find_one({"id": pokemon_id})
        if pokemon:
            results.append(pokemon)
    except ValueError:
        pass  # Not a number, continue with name search
    
    # Search by name across languages
    if len(results) < limit:
        name_results = pokemon_collection.find({
            "$or": [
                {"name.english_lowercase": {"$regex": f".*{query}.*"}},
                {"name.japanese_romanji_lowercase": {"$regex": f".*{query}.*"}},
                {"name.chinese_lowercase": {"$regex": f".*{query}.*"}},
                {"name.french_lowercase": {"$regex": f".*{query}.*"}}
            ]
        }).limit(limit - len(results))
        
        results.extend(list(name_results))
    
    return results 