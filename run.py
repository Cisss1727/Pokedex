"""
Pokedex Web Application Runner
"""
import os
import sys
import subprocess
from pathlib import Path
import webbrowser

def check_directory_exists(directory_path):
    """Check if a directory exists and create it if it doesn't."""
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        return True
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {str(e)}")
        return False

def check_mongodb():
    """Check MongoDB connection."""
    try:
        import pymongo
        from pymongo import MongoClient
        
        # Try to connect to MongoDB with 5 second timeout
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()  # Will throw an exception if unable to connect
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {str(e)}")
        print("Please ensure MongoDB is installed and running on the default port (27017)")
        return False

def check_mongodb_has_data():
    """Simple check if MongoDB has Pokemon data."""
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/")
        db = client.pokedex_db
        pokemon_count = db.pokemon.count_documents({})
        if pokemon_count > 0:
            print(f"MongoDB has {pokemon_count} Pokemon documents")
            return True
        else:
            print("MongoDB has no Pokemon data")
            return False
    except Exception as e:
        print(f"Error checking MongoDB data: {str(e)}")
        return False

def check_static_files():
    """Check if required static files exist and create directories if needed."""
    static_dir = os.path.join("pokedex_app", "static")
    required_dirs = {
        "CSS": os.path.join(static_dir, "css"),
        "JS": os.path.join(static_dir, "js"),
        "Images": os.path.join(static_dir, "images"),
        "Themes": os.path.join(static_dir, "css", "themes"),
        "Sprites": os.path.join(static_dir, "images", "sprites"),
        "Items": os.path.join(static_dir, "images", "items")
    }
    
    all_exist = True
    for name, directory in required_dirs.items():
        if check_directory_exists(directory):
            print(f"✓ {name} directory exists: {directory}")
        else:
            print(f"✗ {name} directory could not be created: {directory}")
            all_exist = False
    
    # Check for favicon.ico
    favicon_path = os.path.join(static_dir, "favicon.ico")
    if not os.path.exists(favicon_path):
        print(f"Creating favicon.ico")
        try:
            # Create a simple text file as a placeholder
            with open(favicon_path, 'w') as f:
                f.write("Favicon placeholder")
            print(f"✓ Created favicon.ico")
        except Exception as e:
            print(f"✗ Failed to create favicon.ico: {str(e)}")
            all_exist = False
    
    return all_exist

def check_pokemon_data():
    """Check if Pokemon data files exist."""
    data_dir = "pokemon-data.json"
    required_files = {
        "Pokedex": os.path.join(data_dir, "pokedex.json"),
        "Moves": os.path.join(data_dir, "moves.json"),
        "Types": os.path.join(data_dir, "types.json"),
        "Items": os.path.join(data_dir, "items.json")
    }
    
    all_exist = True
    for name, file_path in required_files.items():
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"✓ {name} data file found: {file_path}")
        else:
            print(f"✗ {name} data file not found: {file_path}")
            all_exist = False
    
    return all_exist

def import_pokemon_data():
    """Run the import_data.py script to populate MongoDB."""
    print("Starting data import process...")
    try:
        subprocess.run([sys.executable, "pokedex_app/scripts/import_data.py"], check=True)
        print("✓ Data import completed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Data import script failed")
        return False

def main():
    """Main function to run checks and start the app."""
    print("=" * 60)
    print("Starting Pokedex Web Application")
    print("=" * 60)
    
    # Check MongoDB
    if not check_mongodb():
        print("MongoDB check failed. Please ensure MongoDB is installed and running.")
        sys.exit(1)
    
    # Check static files and directories
    check_static_files()
    
    # Check Pokemon data files
    data_files_exist = check_pokemon_data()
    
    # Check if MongoDB has data
    has_mongodb_data = check_mongodb_has_data()
    
    # Ask if the user wants to import data if files exist but MongoDB doesn't have data
    if data_files_exist and not has_mongodb_data:
        print("MongoDB doesn't have all required data.")
        print("Would you like to import/update Pokemon data in MongoDB? (y/n)")
        if input().lower() == 'y':
            if not import_pokemon_data():
                print("Data import failed. App may not work properly.")
    
    # Start the Flask application
    print("Starting Flask application...")
    
    # Display URL but don't open browser automatically
    # This prevents duplicate tabs from opening
    url = "http://localhost:5000"
    print(f"Please open your browser and navigate to: {url}")
    
    # Start Flask app
    from pokedex_app.app import create_app
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 