import os
import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED
from utils import OpenAIClient
from auth import AuthManager
from logging_config import setup_logger, log_request, log_response

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")  # For basic token authentication

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env file")
if not API_AUTH_TOKEN:
    raise RuntimeError("API_AUTH_TOKEN not set in .env file")

# Initialize FastAPI app
app = FastAPI()

# Setup CORS (allow frontend origin, adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logger
logger = setup_logger()

# Data models
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime.datetime

# Dependency for authentication
def get_token_header(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = auth_header.split("Bearer ")[1]
    auth_manager = AuthManager(API_AUTH_TOKEN)
    if not auth_manager.verify_token(token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return token

# Health check endpoint
@app.get("/health_check")
async def health_check():
    return JSONResponse(content={"status": "ok"})

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, token: str = Depends(get_token_header)):
    log_request(logger, request)
    openai_client = OpenAIClient(OPENAI_API_KEY)
    try:
        response_text = await openai_client.generate_response(request.message)
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error communicating with OpenAI API")
    chat_response = ChatResponse(
        response=response_text,
        timestamp=datetime.datetime.utcnow()
    )
    log_response(logger, chat_response)
    return chat_response

# Root endpoint (optional)
@app.get("/")
async def root():
    return JSONResponse(content={"message": "Chatbot backend is running."})