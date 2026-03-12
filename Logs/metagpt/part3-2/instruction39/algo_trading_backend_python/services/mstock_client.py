import requests
from typing import Dict, Any
from fastapi import HTTPException, status
from utils.logger import logger

# Configuration for mStock Type A User APIs
MSTOCK_BASE_URL = "https://api.mstock.com/v1"  # Replace with actual mStock API base URL
MSTOCK_LOGIN_ENDPOINT = "/auth/login"
MSTOCK_LOGOUT_ENDPOINT = "/auth/logout"
MSTOCK_FUNDS_ENDPOINT = "/funds/details"

# These would typically be loaded from environment variables or a config file
MSTOCK_API_CLIENT_ID = "your_client_id"
MSTOCK_API_CLIENT_SECRET = "your_client_secret"

def mstock_login(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate with mStock Type A User API and return the response.
    """
    url = MSTOCK_BASE_URL + MSTOCK_LOGIN_ENDPOINT
    payload = {
        "username": username,
        "password": password,
        "client_id": MSTOCK_API_CLIENT_ID,
        "client_secret": MSTOCK_API_CLIENT_SECRET,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            logger.info(f"mStock login successful for user '{username}'.")
            return data
        else:
            logger.warning(f"mStock login failed for user '{username}': {data.get('error')}")
            return {"success": False, "error": data.get("error", "Unknown error")}
    except requests.RequestException as e:
        logger.error(f"mStock login request error for user '{username}': {e}")
        return {"success": False, "error": str(e)}

def mstock_logout(session_token: str) -> Dict[str, Any]:
    """
    Logout from mStock Type A User API using the session token.
    """
    url = MSTOCK_BASE_URL + MSTOCK_LOGOUT_ENDPOINT
    headers = {
        "Authorization": f"Bearer {session_token}"
    }
    try:
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            logger.info("mStock logout successful.")
            return data
        else:
            logger.warning(f"mStock logout failed: {data.get('error')}")
            return {"success": False, "error": data.get("error", "Unknown error")}
    except requests.RequestException as e:
        logger.error(f"mStock logout request error: {e}")
        return {"success": False, "error": str(e)}

def mstock_get_fund_details(user_id: int) -> Dict[str, Any]:
    """
    Retrieve fund details for a user from mStock Type A User API.
    """
    url = MSTOCK_BASE_URL + MSTOCK_FUNDS_ENDPOINT
    params = {
        "user_id": user_id
    }
    # In a real system, you may need to pass an access token or API key in headers
    headers = {
        "X-Client-Id": MSTOCK_API_CLIENT_ID,
        "X-Client-Secret": MSTOCK_API_CLIENT_SECRET,
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            logger.info(f"mStock fund details fetched for user_id={user_id}.")
            return {
                "success": True,
                "balance": data.get("balance", 0.0),
                "currency": data.get("currency", "USD"),
            }
        else:
            logger.warning(f"mStock fund details fetch failed for user_id={user_id}: {data.get('error')}")
            return {"success": False, "error": data.get("error", "Unknown error")}
    except requests.RequestException as e:
        logger.error(f"mStock fund details request error for user_id={user_id}: {e}")
        return {"success": False, "error": str(e)}