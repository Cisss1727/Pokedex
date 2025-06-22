from flask import Flask
from pokedex_app.app.models.mongodb import mongo
from flask_caching import Cache
from flask_cors import CORS
import os
import sys

# Add parent directory to sys.path to make imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

cache = Cache()

def create_app(config_class=None):
    # Setup static folder path to be one level up from the app directory
    static_folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    template_folder_path = os.path.join(os.path.dirname(__file__), 'templates')
    
    app = Flask(__name__,
               static_folder=static_folder_path,
               template_folder=template_folder_path)
    
    # Load config
    if config_class is None:
        app.config.from_object('pokedex_app.config.Config')
    else:
        app.config.from_object(config_class)
    
    # Initialize extensions
    mongo.init_app(app)
    cache.init_app(app)
    CORS(app)
    
    # Add built-in functions to Jinja environment
    app.jinja_env.globals.update(
        max=max,
        min=min
    )
    
    # Register blueprints
    from pokedex_app.app.routes.main import main_bp
    from pokedex_app.app.routes.pokemon import pokemon_bp
    from pokedex_app.app.routes.search import search_bp
    from pokedex_app.app.routes.api import api_bp
    from pokedex_app.app.routes.team_builder import team_builder_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(pokemon_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(team_builder_bp)
    
    return app 