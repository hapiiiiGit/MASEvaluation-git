import os
import hashlib
import threading
from typing import Optional, Callable
from models.user import UserModel, User
from utils.config import Config
from utils.encryption import Encryption

# For OAuth2
from authlib.integrations.requests_client import OAuth2Session

# For biometric authentication (platform-specific, here as a stub)
def biometric_authenticate() -> bool:
    # Platform-specific biometric authentication logic
    # Return True if successful, False otherwise
    # On mobile, use Android/iOS APIs; on desktop, fallback to password
    return False

class AuthService:
    def __init__(self, config: Config, encryption: Encryption):
        self.config = config
        self.encryption = encryption
        self.user_model = UserModel()
        self.current_user: Optional[User] = None
        self.session_token: Optional[str] = None

        # OAuth2 configuration
        self.oauth_config = {
            'google': {
                'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
                'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
                'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                'scope': 'openid email profile'
            },
            'dropbox': {
                'client_id': os.environ.get('DROPBOX_CLIENT_ID', ''),
                'client_secret': os.environ.get('DROPBOX_CLIENT_SECRET', ''),
                'authorize_url': 'https://www.dropbox.com/oauth2/authorize',
                'token_url': 'https://api.dropboxapi.com/oauth2/token',
                'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                'scope': ''
            }
        }

    def hash_password(self, password: str) -> str:
        # Use SHA256 for password hashing (for demo; use bcrypt/argon2 in production)
        salt = self.config.get('password_salt', 'diverlogbook')
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def get_current_user(self) -> Optional[User]:
        return self.current_user

    def login(self, username_or_email: str, password: str, status_label=None) -> bool:
        password_hash = self.hash_password(password)
        user = self.user_model.authenticate_local(username_or_email, password_hash)
        if user:
            self.current_user = user
            self.session_token = self.encryption.encrypt(user.username + str(user.id))
            self.config.set_current_user_id(user.id)
            if status_label:
                status_label.text = "Login successful!"
            return True
        else:
            if status_label:
                status_label.text = "Invalid credentials or inactive account."
            return False

    def oauth_login(self, provider: str, status_label=None) -> None:
        if provider not in self.oauth_config:
            if status_label:
                status_label.text = f"OAuth provider '{provider}' not supported."
            return

        conf = self.oauth_config[provider]
        oauth = OAuth2Session(
            client_id=conf['client_id'],
            client_secret=conf['client_secret'],
            scope=conf['scope'],
            redirect_uri=conf['redirect_uri']
        )
        # Step 1: Get authorization URL
        auth_url, state = oauth.create_authorization_url(conf['authorize_url'])
        # Step 2: Open URL for user to authenticate (platform-specific)
        import webbrowser
        webbrowser.open(auth_url)
        if status_label:
            status_label.text = "Please complete login in browser and paste the code."

        # Step 3: Prompt user for code (simulate dialog)
        def get_code():
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw()
            code = simpledialog.askstring("OAuth2", "Paste the authorization code here:")
            root.destroy()
            return code

        def finish_oauth():
            code = get_code()
            if not code:
                if status_label:
                    status_label.text = "No code entered."
                return
            token = oauth.fetch_token(
                conf['token_url'],
                code=code,
                client_secret=conf['client_secret']
            )
            # Get user info (Google: id_token, Dropbox: /users/get_current_account)
            if provider == 'google':
                id_token = token.get('id_token')
                import jwt
                userinfo = jwt.decode(id_token, options={"verify_signature": False})
                email = userinfo.get('email')
                oauth_id = userinfo.get('sub')
            elif provider == 'dropbox':
                access_token = token.get('access_token')
                import requests
                resp = requests.post(
                    'https://api.dropboxapi.com/2/users/get_current_account',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                userinfo = resp.json()
                email = userinfo.get('email')
                oauth_id = userinfo.get('account_id')
            else:
                email = None
                oauth_id = None

            user = self.user_model.authenticate_oauth(provider, oauth_id)
            if not user and email:
                # Register new user
                user = self.user_model.create_user(
                    username=email.split('@')[0],
                    email=email,
                    oauth_provider=provider,
                    oauth_id=oauth_id
                )
            if user:
                self.current_user = user
                self.session_token = self.encryption.encrypt(user.username + str(user.id))
                self.config.set_current_user_id(user.id)
                if status_label:
                    status_label.text = "OAuth login successful!"
            else:
                if status_label:
                    status_label.text = "OAuth login failed."

        # Run in thread to avoid blocking UI
        threading.Thread(target=finish_oauth).start()

    def biometric_login(self, status_label=None) -> bool:
        if biometric_authenticate():
            user_id = self.config.get_current_user_id()
            user = self.user_model.get_user_by_id(user_id)
            if user:
                self.current_user = user
                self.session_token = self.encryption.encrypt(user.username + str(user.id))
                if status_label:
                    status_label.text = "Biometric login successful!"
                return True
        if status_label:
            status_label.text = "Biometric authentication failed."
        return False

    def logout(self):
        self.current_user = None
        self.session_token = None
        self.config.set_current_user_id(None)

    def open_registration(self):
        # Implement registration dialog (platform-specific)
        pass

    def open_password_reset(self):
        # Implement password reset dialog (platform-specific)
        pass

    def close(self):
        self.user_model.close()