import os
from fastapi import APIRouter
from pydantic import BaseModel

from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import List

router = APIRouter()

class MessageDict(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_history: List[MessageDict] = []

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@router.post("/chat")
def chat(request: ChatRequest):
    # Setup Chroma Vector Store
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not gemini_api_key:
        return {"response": " Error: Please add your GEMINI_API_KEY to the backend/.env file."}

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=gemini_api_key
    )
    
    try:
        vectorstore = Chroma(
            persist_directory=db_dir,
            embedding_function=embeddings,
            collection_name="chunks_collection"
        )
            
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        system_prompt = (
            "You are a helpful assistant that answers questions about a website the user has scraped.\n"
            "Use the provided context from the scraped website AND the chat history to answer the question.\n"
            "If the answer can be inferred from the chat history (e.g. a follow-up question), use that information too.\n"
            "Only say you don't have enough information if the topic is genuinely not covered in both the context and chat history.\n"
            "Be concise and direct. Format your answer clearly.\n"
            "\n\nScraped Website Context:\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=gemini_api_key
        )
        
        history_msgs = []
        for msg in request.chat_history:
            if msg.content.startswith("Hello! I am URLBot"):
                continue
            if msg.role == 'user':
                history_msgs.append(HumanMessage(content=msg.content))
            else:
                history_msgs.append(AIMessage(content=msg.content))
        
        chain = (
            {
                "context": retriever | format_docs, 
                "input": RunnablePassthrough(),
                "chat_history": lambda x: history_msgs
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        print("Invoking Gemini via LangChain LCEL...")
        response = chain.invoke(request.message)
        return {"response": response}
        
    except Exception as e:
        print("Gemini Failed:", e)
        print("Attempting to fallback to Hugging Face free API...")
        
        if not hf_api_key or hf_api_key == "your_hugging_face_api_token_here":
            return {"response": f" Gemini API Error and no HuggingFace fallback available. Error details: {e}"}
            
        try:
            # Fallback LLM
            fallback_llm = HuggingFaceEndpoint(
                endpoint_url="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=hf_api_key,
                max_new_tokens=256,
            )
            
            fallback_chain = (
                {
                    "context": retriever | format_docs, 
                    "input": RunnablePassthrough(),
                    "chat_history": lambda x: history_msgs
                }
                | prompt
                | fallback_llm
                | StrOutputParser()
            )
            
            response = fallback_chain.invoke(request.message)
            return {"response": "[Fallback HuggingFace Model] " + response}
            
        except Exception as hf_e:
            print("HuggingFace Fallback Failed:", hf_e)
            return {"response": f" Both Gemini and Fallback API failed. Error: {hf_e}"}
