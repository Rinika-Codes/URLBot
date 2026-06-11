import os
import re
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import chunks_collection
from chroma_client import chroma_client

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

def get_relevant_chunks(query, top_n=3):
    try:
        # Get collection dynamically to avoid stale references if recreated
        collection = chroma_client.get_or_create_collection("chunks_collection")
        
        # Avoid error if collection is empty
        if collection.count() == 0:
            return []
        
        results = collection.query(
            query_texts=[query],
            n_results=top_n
        )
        if results and results['documents'] and results['documents'][0]:
            return results['documents'][0]
        return []
    except Exception as e:
        print("Chroma search error:", e)
        return []

@router.post("/chat")
def chat(request: ChatRequest):
    # Gemini requires an API token in the environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"response": "⚠️ Error: Please add your GEMINI_API_KEY to the backend/.env file to enable the AI."}

    # Get relevant context
    relevant_chunks = get_relevant_chunks(request.message)
    context = "\n\n".join(relevant_chunks)
    
    if not context:
        context = "No relevant context found from scraped pages."

    # Prompt construction
    prompt = (
        f"Context from scraped website:\n{context}\n\n"
        f"Question: {request.message}\n"
        f"Answer the question based ONLY on the context above. "
        f"If you don't know the answer from the context, just say 'I don't have enough information from the scraped website.' "
        f"Answer concisely."
    )

    try:
        import google.generativeai as genai
        # Configure Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            answer = response.text.strip()
            return {"response": answer}
        else:
            raise Exception(f"Unexpected empty response from Gemini")
        
    except Exception as e:
        print("Gemini API Error:", e)
        # Final fallback just in case the API fails
        fallback_msg = (
            "⚠️ Gemini API Error. Ensure your API key is correct and valid. "
            "Here is the raw context found from the website instead:\n\n"
        )
        return {"response": fallback_msg + context}
