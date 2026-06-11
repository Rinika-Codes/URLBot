import os
import chromadb

# Ensure the directory exists
db_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
os.makedirs(db_dir, exist_ok=True)

# Initialize a persistent client
chroma_client = chromadb.PersistentClient(path=db_dir)

# Get or create the collection for scraped chunks
chroma_collection = chroma_client.get_or_create_collection(name="chunks_collection")
