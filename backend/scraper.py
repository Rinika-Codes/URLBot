from bs4 import BeautifulSoup
from database import pages_collection, chunks_collection
import uuid
import os

from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def bs4_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return soup.get_text(separator=" ", strip=True)

def crawl_website(url, max_pages=5):
    # Setup chroma database path
    db_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
    
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    api_key = os.getenv("GEMINI_API_KEY")

    # Initialize embedding function
    # Note: ensure GEMINI_API_KEY is in your environment
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2", 
        google_api_key=api_key
    )

    # Clear previous MongoDB collections
    pages_collection.delete_many({})
    chunks_collection.delete_many({})

    # Clear ChromaDB (easiest way is to delete and recreate collection if needed, 
    # but Langchain's Chroma wrapper doesn't have an easy drop_collection exposed in the same way,
    # so we can use persistent client to delete the collection directly)
    import chromadb
    chroma_client = chromadb.PersistentClient(path=db_dir)
    try:
        chroma_client.delete_collection("chunks_collection")
    except Exception:
        pass

    # Load documents lazily to respect max_pages
    loader = RecursiveUrlLoader(url, max_depth=2, extractor=bs4_extractor)
    
    docs = []
    print(f"Starting LangChain crawl on: {url}")
    for doc in loader.lazy_load():
        if len(docs) >= max_pages:
            break
        # Skip small or empty docs
        if len(doc.page_content) > 100:
            docs.append(doc)
            print(f"Crawled: {doc.metadata.get('source')}")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    # Insert raw pages to MongoDB
    all_content = []
    for doc in docs:
        page_url = doc.metadata.get("source", url)
        page_data = {
            "website": url,
            "page_url": page_url,
            "content": doc.page_content[:3000]
        }
        all_content.append(page_data.copy())
        pages_collection.insert_one(page_data)

    # Insert chunks to MongoDB
    for index, split in enumerate(splits):
        page_url = split.metadata.get("source", url)
        chunk_data = {
            "website": url,
            "page_url": page_url,
            "chunk_number": index,
            "chunk_text": split.page_content
        }
        chunks_collection.insert_one(chunk_data)

    # Ingest into ChromaDB using LangChain
    if splits:
        Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=db_dir,
            collection_name="chunks_collection"
        )

    return {
        "pages_crawled": len(docs),
        "content": all_content
    }