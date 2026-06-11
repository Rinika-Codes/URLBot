# URLBot 🚀

URLBot is an AI-powered Retrieval-Augmented Generation (RAG) chatbot that transforms any website into an interactive knowledge base. Simply provide a URL, and the application scrapes the website, processes its content, stores semantic embeddings, and allows users to chat with the extracted information using Google Gemini AI.

## ✨ Features

* 🌐 Scrape content from any public website
* 🤖 Chat with website content using Google Gemini
* 🔍 Semantic search powered by ChromaDB
* 📚 Retrieval-Augmented Generation (RAG) pipeline
* ⚡ FastAPI backend for efficient processing
* 🎨 Responsive React frontend
* 💾 MongoDB integration for data storage

## 🛠️ Tech Stack

### Frontend

* React.js
* Axios
* Tailwind CSS / CSS

### Backend

* FastAPI
* Python

### Databases

* MongoDB
* ChromaDB

### AI & NLP

* Google Gemini API
* Sentence Transformers

### Web Scraping

* BeautifulSoup4
* Requests

## 🏗️ How It Works

1. User enters a website URL.
2. The backend scrapes and extracts website content.
3. Content is cleaned and divided into chunks.
4. Chunks are converted into vector embeddings.
5. Embeddings are stored in ChromaDB.
6. User asks questions about the website.
7. Relevant chunks are retrieved using semantic search.
8. Gemini generates answers based on the retrieved context.

## 📁 Project Structure

```text
URLBot/
├── frontend/
│   ├── src/
│   └── public/
├── backend/
│   ├── routes/
│   ├── services/
│   ├── scraper/
│   └── main.py
├── chroma_db/
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/urlbot.git
cd urlbot
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
MONGODB_URI=your_mongodb_uri
```

Start the backend:

```bash
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🚀 Future Improvements

* PDF and document support
* Multiple website indexing
* User authentication
* Chat history persistence
* Cloud deployment with Docker


