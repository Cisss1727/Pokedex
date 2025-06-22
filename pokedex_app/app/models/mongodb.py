from flask import current_app
from pymongo import MongoClient

class MongoDB:
    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        mongo_uri = app.config.get('MONGO_URI')
        db_name = app.config.get('MONGO_DB_NAME')
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
    
    def get_collection(self, collection_name):
        return self.db[collection_name]

# Create a global instance
mongo = MongoDB() 