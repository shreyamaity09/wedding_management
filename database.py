from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_database():
    try:
        # Replace with your MongoDB connection string if using MongoDB Atlas
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Test connection
        client.admin.command('ping')
        print("Connected successfully to MongoDB!")
        return client["wedding_db"]
    except ConnectionFailure:
        print("Error: Could not connect to MongoDB. Ensure your MongoDB service is running.")
        return None

# Export database instance
db = get_database()