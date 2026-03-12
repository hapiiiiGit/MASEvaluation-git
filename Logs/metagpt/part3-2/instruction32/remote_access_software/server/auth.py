import logging
from typing import Dict, Optional
import time

# For OAuth2
from authlib.integrations.requests_client import OAuth2Session

# For MFA (simple TOTP implementation)
import pyotp

class AuthProvider:
    """
    Handles authentication for the remote access server.
    Supports OAuth2 and optional multi-factor authentication (MFA).
    """

    def __init__(self, config: Dict):
        self.logger = logging.getLogger("AuthProvider")
        self.oauth_config = config.get("oauth", {})
        self.mfa_config = config.get("mfa", {})
        self.users_mfa_secrets = {}  # user_id -> mfa_secret

    def authenticate_oauth(self, token: str) -> Optional[str]:
        """
        Authenticate user using OAuth2 token.
        Returns user_id if successful, None otherwise.
        """
        # Example: Google OAuth2 token validation
        provider = self.oauth_config.get("provider", "google")
        client_id = self.oauth_config.get("client_id")
        client_secret = self.oauth_config.get("client_secret")
        userinfo_endpoint = self.oauth_config.get("userinfo_endpoint")

        if not all([provider, client_id, client_secret, userinfo_endpoint]):
            self.logger.error("OAuth2 configuration incomplete.")
            return None

        try:
            session = OAuth2Session(client_id, client_secret, token={"access_token": token, "token_type": "Bearer"})
            resp = session.get(userinfo_endpoint)
            if resp.status_code == 200:
                userinfo = resp.json()
                user_id = userinfo.get("sub") or userinfo.get("id") or userinfo.get("email")
                self.logger.info(f"OAuth2 authentication successful for user: {user_id}")
                return user_id
            else:
                self.logger.warning(f"OAuth2 authentication failed: {resp.text}")
                return None
        except Exception as e:
            self.logger.error(f"OAuth2 authentication error: {e}")
            return None

    def is_mfa_enabled(self, user_id: str) -> bool:
        """
        Check if MFA is enabled for the user.
        """
        return user_id in self.users_mfa_secrets

    def enable_mfa(self, user_id: str) -> str:
        """
        Enable MFA for a user and return the secret.
        """
        secret = pyotp.random_base32()
        self.users_mfa_secrets[user_id] = secret
        self.logger.info(f"MFA enabled for user {user_id}")
        return secret

    def disable_mfa(self, user_id: str):
        """
        Disable MFA for a user.
        """
        if user_id in self.users_mfa_secrets:
            del self.users_mfa_secrets[user_id]
            self.logger.info(f"MFA disabled for user {user_id}")

    def authenticate_mfa(self, user_id: str, code: str) -> bool:
        """
        Authenticate user using MFA (TOTP).
        Returns True if successful, False otherwise.
        """
        secret = self.users_mfa_secrets.get(user_id)
        if not secret:
            self.logger.warning(f"MFA not enabled for user {user_id}")
            return False
        totp = pyotp.TOTP(secret)
        result = totp.verify(code, valid_window=1)
        if result:
            self.logger.info(f"MFA authentication successful for user {user_id}")
        else:
            self.logger.warning(f"MFA authentication failed for user {user_id}")
        return result