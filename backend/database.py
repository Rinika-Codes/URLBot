import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)

db = client["campusgpt"]

pages_collection = db["pages"]
chunks_collection = db["chunks"]