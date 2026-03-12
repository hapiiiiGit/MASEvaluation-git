import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class Encryption:
    """
    Encryption utilities for secure data storage and transmission.
    Uses Fernet symmetric encryption, PBKDF2 for key derivation, and SHA256 for password hashing.
    """

    def __init__(self, config):
        self.config = config
        self._key = self._get_or_generate_key()

    def _get_or_generate_key(self):
        """
        Get encryption key from config or generate a new one.
        Uses PBKDF2HMAC to derive a key from a passphrase and salt.
        """
        passphrase = self.config.get('encryption_passphrase', 'diverlogbook_default_passphrase')
        salt = self.config.get('encryption_salt', b'diverlogbook_salt')
        if isinstance(salt, str):
            salt = salt.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))
        return key

    def encrypt(self, data: str) -> str:
        """
        Encrypts a string and returns the base64-encoded ciphertext.
        """
        f = Fernet(self._key)
        token = f.encrypt(data.encode('utf-8'))
        return token.decode('utf-8')

    def decrypt(self, token: str) -> str:
        """
        Decrypts a base64-encoded ciphertext and returns the original string.
        """
        f = Fernet(self._key)
        data = f.decrypt(token.encode('utf-8'))
        return data.decode('utf-8')

    def hash_password(self, password: str) -> str:
        """
        Hashes a password using SHA256. For production, use bcrypt or argon2.
        """
        salt = self.config.get('password_salt', 'diverlogbook')
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

    def generate_token(self, length: int = 32) -> str:
        """
        Generates a secure random token for session management.
        """
        return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')

    def encrypt_file(self, input_path: str, output_path: str):
        """
        Encrypts a file and writes the encrypted data to output_path.
        """
        f = Fernet(self._key)
        with open(input_path, 'rb') as infile:
            data = infile.read()
        encrypted = f.encrypt(data)
        with open(output_path, 'wb') as outfile:
            outfile.write(encrypted)

    def decrypt_file(self, input_path: str, output_path: str):
        """
        Decrypts a file and writes the decrypted data to output_path.
        """
        f = Fernet(self._key)
        with open(input_path, 'rb') as infile:
            encrypted = infile.read()
        decrypted = f.decrypt(encrypted)
        with open(output_path, 'wb') as outfile:
            outfile.write(decrypted)