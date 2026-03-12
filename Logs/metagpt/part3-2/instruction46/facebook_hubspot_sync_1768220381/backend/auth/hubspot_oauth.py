from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import requests
from urllib.parse import urlencode

from backend.utils.logger import get_logger

logger = get_logger(__name__)

HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
HUBSPOT_REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI", "http://localhost:8000/auth/hubspot/callback")
HUBSPOT_AUTH_BASE = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

router = APIRouter()

class HubSpotOAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "contacts deals oauth",
            "response_type": "code"
        }
        if state:
            params["state"] = state
        return f"{HUBSPOT_AUTH_BASE}?{urlencode(params)}"

    def fetch_token(self, code: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(HUBSPOT_TOKEN_URL, data=data, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch HubSpot token: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to fetch HubSpot token")
        return response.json()

    def refresh_token(self, refresh_token: str) -> dict:
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "refresh_token": refresh_token
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(HUBSPOT_TOKEN_URL, data=data, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to refresh HubSpot token: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to refresh HubSpot token")
        return response.json()

hubspot_oauth = HubSpotOAuth(
    client_id=HUBSPOT_CLIENT_ID,
    client_secret=HUBSPOT_CLIENT_SECRET,
    redirect_uri=HUBSPOT_REDIRECT_URI
)

class TokenRequest(BaseModel):
    code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.get("/login")
async def hubspot_login(state: Optional[str] = None):
    """
    Redirect user to HubSpot OAuth login.
    """
    auth_url = hubspot_oauth.get_auth_url(state)
    logger.info(f"Redirecting to HubSpot OAuth: {auth_url}")
    return RedirectResponse(auth_url)

@router.get("/callback")
async def hubspot_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """
    Handle HubSpot OAuth callback.
    """
    if error:
        logger.error(f"HubSpot OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"HubSpot OAuth error: {error}")
    if not code:
        logger.error("No code provided in HubSpot OAuth callback.")
        raise HTTPException(status_code=400, detail="No code provided in callback.")
    try:
        token_data = hubspot_oauth.fetch_token(code)
        logger.info("HubSpot OAuth token fetched successfully.")
        # In production, store token_data securely (e.g., DB, encrypted session)
        return JSONResponse(token_data)
    except Exception as e:
        logger.error(f"Exception in HubSpot OAuth callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete HubSpot OAuth.")

@router.post("/token")
async def hubspot_token(request: TokenRequest):
    """
    Exchange code for access token.
    """
    try:
        token_data = hubspot_oauth.fetch_token(request.code)
        logger.info("HubSpot OAuth token fetched via /token endpoint.")
        return token_data
    except Exception as e:
        logger.error(f"Exception in /token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch HubSpot token.")

@router.post("/refresh")
async def hubspot_refresh_token(request: RefreshTokenRequest):
    """
    Exchange refresh token for new access token.
    """
    try:
        token_data = hubspot_oauth.refresh_token(request.refresh_token)
        logger.info("HubSpot OAuth token refreshed successfully.")
        return token_data
    except Exception as e:
        logger.error(f"Exception in /refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh HubSpot token.")