from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routes import chat
from database import db
from scraper import crawl_website
from database import pages_collection
from database import chunks_collection
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/")
def home():
    return {"message": "CampusGPT backend running"}

@app.get("/testdb")
def test_db():
    db.test.insert_one({"msg": "hello"})
    return {"message": "Inserted into MongoDB"}


class ScrapeRequest(BaseModel):
    url: str
    max_pages: int = 5

@app.post("/scrape")
def scrape(request: ScrapeRequest):
    try:
        data = crawl_website(
            request.url,
            max_pages=request.max_pages
        )
        return data
    except Exception as e:
        import traceback
        import datetime
        log_path = os.path.join(os.path.dirname(__file__), "error.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Scrape Exception at {datetime.datetime.now()} ---\n")
            traceback.print_exc(file=f)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pages")
def get_pages():

    pages_cursor = pages_collection.find({}, {"_id": 0})

    pages = []

    for page in pages_cursor:
        pages.append(page)

    return pages


@app.get("/chunks")
def get_chunks():

    chunks = list(
        chunks_collection.find(
            {},
            {"_id": 0}
        )
    )

    return chunks