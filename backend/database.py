from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["campusgpt"]

pages_collection = db["pages"]
chunks_collection = db["chunks"]