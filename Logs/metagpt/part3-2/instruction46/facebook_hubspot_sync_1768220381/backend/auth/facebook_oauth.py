from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import requests
from urllib.parse import urlencode

from backend.utils.logger import get_logger

logger = get_logger(__name__)

FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback")
FACEBOOK_AUTH_BASE = "https://www.facebook.com/v18.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"

router = APIRouter()

class FacebookOAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "ads_read,ads_management,business_management,email,public_profile",
            "response_type": "code"
        }
        if state:
            params["state"] = state
        return f"{FACEBOOK_AUTH_BASE}?{urlencode(params)}"

    def fetch_token(self, code: str) -> dict:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "client_secret": self.client_secret,
            "code": code
        }
        response = requests.get(FACEBOOK_TOKEN_URL, params=params)
        if response.status_code != 200:
            logger.error(f"Failed to fetch Facebook token: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to fetch Facebook token")
        return response.json()

    def refresh_token(self, refresh_token: str) -> dict:
        # Facebook uses long-lived tokens, not refresh tokens, but we can exchange for a long-lived token
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": refresh_token
        }
        response = requests.get(FACEBOOK_TOKEN_URL, params=params)
        if response.status_code != 200:
            logger.error(f"Failed to refresh Facebook token: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to refresh Facebook token")
        return response.json()

facebook_oauth = FacebookOAuth(
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_CLIENT_SECRET,
    redirect_uri=FACEBOOK_REDIRECT_URI
)

class TokenRequest(BaseModel):
    code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.get("/login")
async def facebook_login(state: Optional[str] = None):
    """
    Redirect user to Facebook OAuth login.
    """
    auth_url = facebook_oauth.get_auth_url(state)
    logger.info(f"Redirecting to Facebook OAuth: {auth_url}")
    return RedirectResponse(auth_url)

@router.get("/callback")
async def facebook_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """
    Handle Facebook OAuth callback.
    """
    if error:
        logger.error(f"Facebook OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"Facebook OAuth error: {error}")
    if not code:
        logger.error("No code provided in Facebook OAuth callback.")
        raise HTTPException(status_code=400, detail="No code provided in callback.")
    try:
        token_data = facebook_oauth.fetch_token(code)
        logger.info("Facebook OAuth token fetched successfully.")
        # In production, store token_data securely (e.g., DB, encrypted session)
        return JSONResponse(token_data)
    except Exception as e:
        logger.error(f"Exception in Facebook OAuth callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete Facebook OAuth.")

@router.post("/token")
async def facebook_token(request: TokenRequest):
    """
    Exchange code for access token.
    """
    try:
        token_data = facebook_oauth.fetch_token(request.code)
        logger.info("Facebook OAuth token fetched via /token endpoint.")
        return token_data
    except Exception as e:
        logger.error(f"Exception in /token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Facebook token.")

@router.post("/refresh")
async def facebook_refresh_token(request: RefreshTokenRequest):
    """
    Exchange short-lived token for long-lived token.
    """
    try:
        token_data = facebook_oauth.refresh_token(request.refresh_token)
        logger.info("Facebook OAuth token refreshed successfully.")
        return token_data
    except Exception as e:
        logger.error(f"Exception in /refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh Facebook token.")