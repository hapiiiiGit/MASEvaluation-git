import json
import sqlite3
from typing import Dict, List, Optional, Any
import os
import hashlib

class ClientManager:
    """
    Handles user authentication, client management, and data partitioning for multi-client support.
    Provides:
        - authenticate(username, password) -> str
        - get_clients() -> list
        - add_client(client_info: dict)
    """

    def __init__(self, storage):
        """
        storage: instance of Storage class (must provide get_storage_type(), get_storage_path())
        """
        self.storage = storage
        self.storage_type = self.storage.get_storage_type()
        self.storage_path = self.storage.get_storage_path()
        self._init_db()

    def _init_db(self):
        if self.storage_type == "sqlite":
            self.conn = sqlite3.connect(self.storage_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    info TEXT
                )
            """)
            self.conn.commit()
        elif self.storage_type == "json":
            if not os.path.exists(self.storage_path):
                with open(self.storage_path, "w") as f:
                    json.dump({"clients": {}}, f)
            else:
                with open(self.storage_path, "r") as f:
                    db = json.load(f)
                if "clients" not in db:
                    db["clients"] = {}
                    with open(self.storage_path, "w") as f:
                        json.dump(db, f, indent=2)
        else:
            raise ValueError("Unsupported storage type: {}".format(self.storage_type))

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticates a user and returns the client_id if successful, else None.
        """
        password_hash = self._hash_password(password)
        if self.storage_type == "sqlite":
            self.cursor.execute(
                "SELECT client_id, password_hash FROM clients WHERE username=?",
                (username,)
            )
            row = self.cursor.fetchone()
            if row and row[1] == password_hash:
                return row[0]
            return None
        elif self.storage_type == "json":
            with open(self.storage_path, "r") as f:
                db = json.load(f)
            for client_id, client in db.get("clients", {}).items():
                if client.get("username") == username and client.get("password_hash") == password_hash:
                    return client_id
            return None

    def get_clients(self) -> List[str]:
        """
        Returns a list of client IDs.
        """
        if self.storage_type == "sqlite":
            self.cursor.execute("SELECT client_id FROM clients")
            return [row[0] for row in self.cursor.fetchall()]
        elif self.storage_type == "json":
            with open(self.storage_path, "r") as f:
                db = json.load(f)
            return list(db.get("clients", {}).keys())

    def add_client(self, client_info: Dict[str, Any]):
        """
        Adds a new client. client_info must include 'client_id', 'username', 'password', and optionally other info.
        """
        client_id = client_info.get("client_id")
        username = client_info.get("username")
        password = client_info.get("password")
        info = {k: v for k, v in client_info.items() if k not in ["client_id", "username", "password"]}
        password_hash = self._hash_password(password)
        if not client_id or not username or not password:
            raise ValueError("client_id, username, and password are required to add a client.")

        if self.storage_type == "sqlite":
            try:
                self.cursor.execute(
                    "INSERT INTO clients (client_id, username, password_hash, info) VALUES (?, ?, ?, ?)",
                    (client_id, username, password_hash, json.dumps(info))
                )
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Failed to add client: {str(e)}")
        elif self.storage_type == "json":
            with open(self.storage_path, "r") as f:
                db = json.load(f)
            if client_id in db.get("clients", {}):
                raise ValueError("Client ID already exists.")
            for cid, client in db.get("clients", {}).items():
                if client.get("username") == username:
                    raise ValueError("Username already exists.")
            db["clients"][client_id] = {
                "username": username,
                "password_hash": password_hash,
                "info": info
            }
            with open(self.storage_path, "w") as f:
                json.dump(db, f, indent=2)

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()