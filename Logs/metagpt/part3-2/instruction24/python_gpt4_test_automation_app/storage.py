import json
import sqlite3
import os
from typing import Dict, Any, Optional

class Storage:
    """
    Handles saving and loading data for each client using SQLite or JSON as the local storage backend.
    Provides:
        - save_data(client_id: str, data: dict)
        - load_data(client_id: str) -> dict
        - set_storage_type(type: str)
        - get_storage_type() -> str
        - get_storage_path() -> str
    """

    def __init__(self, storage_type: str = "sqlite", storage_path: str = "storage.db"):
        self._storage_type = storage_type.lower()
        self._storage_path = storage_path
        if self._storage_type == "sqlite":
            self._init_sqlite()
        elif self._storage_type == "json":
            self._init_json()
        else:
            raise ValueError(f"Unsupported storage type: {self._storage_type}")

    def _init_sqlite(self):
        self.conn = sqlite3.connect(self._storage_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_data (
                client_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        self.conn.commit()

    def _init_json(self):
        if not os.path.exists(self._storage_path):
            with open(self._storage_path, "w") as f:
                json.dump({}, f)

    def save_data(self, client_id: str, data: Dict[str, Any]):
        """
        Saves data for the given client_id.
        If data already exists, it updates/merges the new data.
        """
        if self._storage_type == "sqlite":
            # Load existing data if any
            self.cursor.execute("SELECT data FROM client_data WHERE client_id=?", (client_id,))
            row = self.cursor.fetchone()
            if row:
                existing_data = json.loads(row[0])
                existing_data.update(data)
                data_to_store = json.dumps(existing_data)
                self.cursor.execute("UPDATE client_data SET data=? WHERE client_id=?", (data_to_store, client_id))
            else:
                data_to_store = json.dumps(data)
                self.cursor.execute("INSERT INTO client_data (client_id, data) VALUES (?, ?)", (client_id, data_to_store))
            self.conn.commit()
        elif self._storage_type == "json":
            with open(self._storage_path, "r") as f:
                db = json.load(f)
            if client_id in db:
                db[client_id].update(data)
            else:
                db[client_id] = data
            with open(self._storage_path, "w") as f:
                json.dump(db, f, indent=2)

    def load_data(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Loads and returns data for the given client_id.
        Returns None if no data is found.
        """
        if self._storage_type == "sqlite":
            self.cursor.execute("SELECT data FROM client_data WHERE client_id=?", (client_id,))
            row = self.cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except Exception:
                    return None
            return None
        elif self._storage_type == "json":
            if not os.path.exists(self._storage_path):
                return None
            with open(self._storage_path, "r") as f:
                db = json.load(f)
            return db.get(client_id, None)

    def set_storage_type(self, type: str):
        """
        Changes the storage type (sqlite or json). Re-initializes the backend.
        """
        type = type.lower()
        if type not in ["sqlite", "json"]:
            raise ValueError("Storage type must be 'sqlite' or 'json'.")
        self._storage_type = type
        if type == "sqlite":
            self._init_sqlite()
        else:
            self._init_json()

    def get_storage_type(self) -> str:
        """
        Returns the current storage type.
        """
        return self._storage_type

    def get_storage_path(self) -> str:
        """
        Returns the current storage path.
        """
        return self._storage_path

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()