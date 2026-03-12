import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from openai_client import get_chatbot_response

# Load environment variables from .env file if present
load_dotenv()

# FastAPI app initialization
app = FastAPI(
    title="Azure Chatbot Backend",
    description="Backend for web chatbot interfacing with OpenAI API",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """
    Receives a user message, sends it to OpenAI API, and returns the chatbot response.
    """
    user_message = chat_request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        bot_response = await get_chatbot_response(user_message)
        return ChatResponse(response=bot_response)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error communicating with OpenAI API: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"status": "ok", "message": "Azure Chatbot Backend is running."}