from fastapi import FastAPI
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

    data = crawl_website(
        request.url,
        max_pages=request.max_pages
    )

    return data

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