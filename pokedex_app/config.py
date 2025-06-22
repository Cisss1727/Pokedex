"""
Configuration settings for the Pokedex Web Application
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'pokedex_db')
    
    # Cache settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API settings
    JSON_SORT_KEYS = False
    
    # Path to Pokemon data JSON files
    POKEMON_DATA_PATH = os.environ.get('POKEMON_DATA_PATH', 'pokemon-data.json')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # In production, ensure a strong secret key is set
    if os.environ.get('SECRET_KEY') == 'dev-key-change-in-production':
        raise ValueError(
            'In production mode, SECRET_KEY must be set as an environment variable'
        )

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_DB_NAME = 'pokedex_test_db'
    WTF_CSRF_ENABLED = False
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 