import logging
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

class SecurityManager:
    """
    Implements AES-256 encryption and decryption for secure remote access.
    """

    def __init__(self, config: Optional[dict] = None):
        self.logger = logging.getLogger("SecurityManager")
        self.config = config or {}
        self.key = self._get_key_from_config(self.config)
        if not self.key or len(self.key) != 32:
            self.logger.warning("No valid AES-256 key found in config, generating a random key.")
            self.key = os.urandom(32)  # 256 bits

    def _get_key_from_config(self, config: dict) -> Optional[bytes]:
        key_hex = config.get("aes256_key")
        if key_hex:
            try:
                key_bytes = bytes.fromhex(key_hex)
                if len(key_bytes) == 32:
                    return key_bytes
                else:
                    self.logger.error("AES-256 key in config is not 32 bytes.")
            except Exception as e:
                self.logger.error(f"Failed to parse AES-256 key from config: {e}")
        return None

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts data using AES-256-CBC.
        Returns IV + ciphertext.
        """
        iv = os.urandom(16)  # AES block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        self.logger.debug("Data encrypted using AES-256-CBC.")
        return iv + ciphertext

    def decrypt(self, data: bytes) -> Optional[bytes]:
        """
        Decrypts data using AES-256-CBC.
        Expects IV + ciphertext.
        Returns plaintext or None if decryption fails.
        """
        if len(data) < 16:
            self.logger.error("Data too short to contain IV and ciphertext.")
            return None
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        try:
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            self.logger.debug("Data decrypted using AES-256-CBC.")
            return plaintext
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return None

    def get_key(self) -> bytes:
        """
        Returns the AES-256 key in use.
        """
        return self.key