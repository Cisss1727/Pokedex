import json
import os
import sys
from pathlib import Path
from pymongo import MongoClient

# Add parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# MongoDB connection settings
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('MONGO_DB_NAME', 'pokedex_db')

# Path to JSON files - use the correct path
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'pokemon-data.json')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
pokemon_collection = db['pokemon']
types_collection = db['types']
moves_collection = db['moves']
items_collection = db['items']
generations_collection = db['generations']

def determine_generation(pokemon_id):
    """Determine the generation of a Pokémon based on its ID."""
    if pokemon_id <= 151:
        return 1
    elif pokemon_id <= 251:
        return 2
    elif pokemon_id <= 386:
        return 3
    elif pokemon_id <= 493:
        return 4
    elif pokemon_id <= 649:
        return 5
    elif pokemon_id <= 721:
        return 6
    elif pokemon_id <= 809:
        return 7
    elif pokemon_id <= 905:
        return 8
    else:
        return 9

def is_legendary(pokemon_id, pokemon_name):
    """Determine if a Pokémon is legendary based on its ID or name."""
    legendary_ids = [
        144, 145, 146, 150, 
        243, 244, 245, 249, 250,
        377, 378, 379, 380, 381, 382, 383, 384,
        483, 484, 487, 
        638, 639, 640, 641, 642, 643, 644, 645, 646, 
        716, 717, 718, 
        785, 786, 787, 788, 791, 792, 793, 794, 795, 796, 797, 798, 
        888, 889, 890, 
        898, 905
    ]
    
    legendary_names = [
        "Articuno", "Zapdos", "Moltres", "Mewtwo", "Lugia", "Ho-Oh",
        "Entei", "Raikou", "Suicune", 
        "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza",
        "Dialga", "Palkia", "Giratina", 
        "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem",
        "Xerneas", "Yveltal", "Zygarde", 
        "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Solgaleo", "Lunala", "Necrozma", "Zacian", "Zamazenta", "Eternatus"
    ]
    
    return pokemon_id in legendary_ids or pokemon_name in legendary_names

def is_mythical(pokemon_id, pokemon_name):
    """Determine if a Pokémon is mythical based on its ID or name."""
    mythical_ids = [
        151, 251, 385, 386, 489, 490, 491, 492, 493,
        494, 647, 648, 649, 719, 720, 721, 801, 802, 
        807, 808, 809, 893
    ]
    
    mythical_names = [
        "Mew", "Celebi", "Jirachi", "Deoxys", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus",
        "Victini", "Keldeo", "Meloetta", "Genesect", "Diancie", "Hoopa", "Volcanion", "Magearna", "Marshadow",
        "Zeraora", "Meltan", "Melmetal", "Zarude"
    ]
    
    return pokemon_id in mythical_ids or pokemon_name in mythical_names

def setup_generations():
    """Set up generation data in the database."""
    generations = [
        {
            'id': 1,
            'name': 'Generation I',
            'region': 'Kanto',
            'games': ['Red', 'Blue', 'Yellow']
        },
        {
            'id': 2,
            'name': 'Generation II',
            'region': 'Johto',
            'games': ['Gold', 'Silver', 'Crystal']
        },
        {
            'id': 3,
            'name': 'Generation III',
            'region': 'Hoenn',
            'games': ['Ruby', 'Sapphire', 'Emerald', 'FireRed', 'LeafGreen']
        },
        {
            'id': 4,
            'name': 'Generation IV',
            'region': 'Sinnoh',
            'games': ['Diamond', 'Pearl', 'Platinum', 'HeartGold', 'SoulSilver']
        },
        {
            'id': 5,
            'name': 'Generation V',
            'region': 'Unova',
            'games': ['Black', 'White', 'Black 2', 'White 2']
        },
        {
            'id': 6,
            'name': 'Generation VI',
            'region': 'Kalos',
            'games': ['X', 'Y', 'Omega Ruby', 'Alpha Sapphire']
        },
        {
            'id': 7,
            'name': 'Generation VII',
            'region': 'Alola',
            'games': ['Sun', 'Moon', 'Ultra Sun', 'Ultra Moon', "Let's Go, Pikachu!", "Let's Go, Eevee!"]
        },
        {
            'id': 8,
            'name': 'Generation VIII',
            'region': 'Galar',
            'games': ['Sword', 'Shield', 'Brilliant Diamond', 'Shining Pearl', 'Legends: Arceus']
        },
        {
            'id': 9,
            'name': 'Generation IX',
            'region': 'Paldea',
            'games': ['Scarlet', 'Violet']
        }
    ]
    
    if generations_collection.count_documents({}) == 0:
        generations_collection.insert_many(generations)
        print(f"Inserted {len(generations)} generations")
    else:
        print("Generations collection already exists, skipping...")

def import_pokemon_data():
    """Import Pokémon data from pokedex.json."""
    pokemon_file = os.path.join(JSON_PATH, 'pokedex.json')
    
    if not os.path.exists(pokemon_file):
        print(f"Error: {pokemon_file} not found")
        return
    
    try:
        with open(pokemon_file, 'r', encoding='utf-8') as f:
            pokemon_data = json.load(f)
        
        # Drop existing collection if it exists
        pokemon_collection.drop()
        
        # Process each Pokémon entry
        for pokemon in pokemon_data:
            # Add generation field
            generation = determine_generation(pokemon['id'])
            pokemon['generation'] = generation
            
            # Add legendary/mythical flags
            pokemon_name = pokemon['name']['english']
            pokemon['is_legendary'] = is_legendary(pokemon['id'], pokemon_name)
            pokemon['is_mythical'] = is_mythical(pokemon['id'], pokemon_name)
        
        # Insert all Pokémon data
        pokemon_collection.insert_many(pokemon_data)
        print(f"Inserted {len(pokemon_data)} Pokémon")
        
    except Exception as e:
        print(f"Error importing Pokémon data: {e}")

def import_types_data():
    """Import type data from types.json."""
    types_file = os.path.join(JSON_PATH, 'types.json')
    
    if not os.path.exists(types_file):
        print(f"Error: {types_file} not found")
        return
    
    try:
        with open(types_file, 'r', encoding='utf-8') as f:
            types_data = json.load(f)
        
        # Drop existing collection if it exists
        types_collection.drop()
        
        # Add color field for UI
        type_colors = {
            "Normal": "#A8A77A",
            "Fire": "#EE8130",
            "Water": "#6390F0",
            "Electric": "#F7D02C",
            "Grass": "#7AC74C",
            "Ice": "#96D9D6",
            "Fighting": "#C22E28",
            "Poison": "#A33EA1",
            "Ground": "#E2BF65",
            "Flying": "#A98FF3",
            "Psychic": "#F95587",
            "Bug": "#A6B91A",
            "Rock": "#B6A136",
            "Ghost": "#735797",
            "Dragon": "#6F35FC",
            "Dark": "#705746",
            "Steel": "#B7B7CE",
            "Fairy": "#D685AD"
        }
        
        for type_entry in types_data:
            type_entry['color'] = type_colors.get(type_entry['english'], "#777777")
        
        # Insert all type data
        types_collection.insert_many(types_data)
        print(f"Inserted {len(types_data)} types")
        
    except Exception as e:
        print(f"Error importing type data: {e}")

def import_moves_data():
    """Import move data from moves.json."""
    moves_file = os.path.join(JSON_PATH, 'moves.json')
    
    if not os.path.exists(moves_file):
        print(f"Error: {moves_file} not found")
        return
    
    try:
        with open(moves_file, 'r', encoding='utf-8') as f:
            moves_data = json.load(f)
        
        # Drop existing collection if it exists
        moves_collection.drop()
        
        # Insert all move data
        moves_collection.insert_many(moves_data)
        print(f"Inserted {len(moves_data)} moves")
        
    except Exception as e:
        print(f"Error importing move data: {e}")

def import_items_data():
    """Import item data from items.json."""
    items_file = os.path.join(JSON_PATH, 'items.json')
    
    if not os.path.exists(items_file):
        print(f"Error: {items_file} not found")
        return
    
    try:
        with open(items_file, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
        
        # Drop existing collection if it exists
        items_collection.drop()
        
        # Insert all item data
        items_collection.insert_many(items_data)
        print(f"Inserted {len(items_data)} items")
        
    except Exception as e:
        print(f"Error importing item data: {e}")

if __name__ == "__main__":
    print("Starting data import...")
    
    # Create indexes for collections
    pokemon_collection.create_index('id', unique=True)
    pokemon_collection.create_index('name.english')
    pokemon_collection.create_index('type')
    pokemon_collection.create_index('generation')
    
    # Import data
    setup_generations()
    import_pokemon_data()
    import_types_data()
    import_moves_data()
    import_items_data()
    
    print("Data import completed!") 