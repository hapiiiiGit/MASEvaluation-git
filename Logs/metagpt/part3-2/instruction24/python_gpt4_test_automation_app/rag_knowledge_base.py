import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
import os

class RAGKnowledgeBase:
    """
    Handles RAG knowledge base operations:
    - log_test_data(client_id: str, input_data: dict, output_data: dict, errors: list)
    - retrieve_similar_cases(query: str, client_id: str) -> list
    - improve_input_generation(client_id: str) -> dict

    Uses local storage (SQLite/JSON) for per-client data isolation.
    """

    def __init__(self, storage):
        """
        storage: instance of Storage class (must provide get_storage_type(), get_storage_path())
        """
        self.storage = storage
        self.storage_type = self.storage.get_storage_type()
        self.storage_path = self.storage.get_storage_path()
        if self.storage_type == "sqlite":
            self._init_sqlite_db()
        elif self.storage_type == "json":
            self._init_json_db()
        else:
            raise ValueError("Unsupported storage type: {}".format(self.storage_type))

    # --- SQLite Implementation ---
    def _init_sqlite_db(self):
        self.conn = sqlite3.connect(self.storage_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_kb (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                errors TEXT
            )
        """)
        self.conn.commit()

    # --- JSON Implementation ---
    def _init_json_db(self):
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump({}, f)

    def log_test_data(self, client_id: str, input_data: Dict[str, Any], output_data: Dict[str, Any], errors: List[Dict[str, str]]):
        """
        Logs test data (input, output, errors) for a client into the knowledge base.
        """
        if self.storage_type == "sqlite":
            self.cursor.execute(
                "INSERT INTO rag_kb (client_id, input_data, output_data, errors) VALUES (?, ?, ?, ?)",
                (client_id, json.dumps(input_data), json.dumps(output_data), json.dumps(errors))
            )
            self.conn.commit()
        elif self.storage_type == "json":
            with open(self.storage_path, "r") as f:
                db = json.load(f)
            if client_id not in db:
                db[client_id] = []
            db[client_id].append({
                "input_data": input_data,
                "output_data": output_data,
                "errors": errors
            })
            with open(self.storage_path, "w") as f:
                json.dump(db, f, indent=2)

    def retrieve_similar_cases(self, query: str, client_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves similar cases from the knowledge base for a given query and client.
        For simplicity, matches query against error descriptions.
        """
        results = []
        if self.storage_type == "sqlite":
            self.cursor.execute(
                "SELECT input_data, output_data, errors FROM rag_kb WHERE client_id=?",
                (client_id,)
            )
            rows = self.cursor.fetchall()
            for input_data, output_data, errors in rows:
                error_list = json.loads(errors)
                for error in error_list:
                    if query.lower() in error.get("description", "").lower():
                        results.append({
                            "input_data": json.loads(input_data),
                            "output_data": json.loads(output_data),
                            "error": error
                        })
        elif self.storage_type == "json":
            with open(self.storage_path, "r") as f:
                db = json.load(f)
            for case in db.get(client_id, []):
                for error in case.get("errors", []):
                    if query.lower() in error.get("description", "").lower():
                        results.append({
                            "input_data": case.get("input_data", {}),
                            "output_data": case.get("output_data", {}),
                            "error": error
                        })
        return results

    def improve_input_generation(self, client_id: str) -> Dict[str, Any]:
        """
        Suggests improved input generation based on historical errors for the client.
        Returns a dict of suggestions (e.g., columns with frequent errors).
        """
        error_count = {}
        if self.storage_type == "sqlite":
            self.cursor.execute(
                "SELECT input_data, output_data, errors FROM rag_kb WHERE client_id=?",
                (client_id,)
            )
            rows = self.cursor.fetchall()
            for input_data, output_data, errors in rows:
                error_list = json.loads(errors)
                for error in error_list:
                    key = error.get("category", "UnknownError")
                    error_count[key] = error_count.get(key, 0) + 1
        elif self.storage_type == "json":
            with open(self.storage_path, "r") as f:
                db = json.load(f)
            for case in db.get(client_id, []):
                for error in case.get("errors", []):
                    key = error.get("category", "UnknownError")
                    error_count[key] = error_count.get(key, 0) + 1

        # Suggest improvements based on most frequent error categories
        if not error_count:
            return {"suggestion": "No historical errors found. No improvement needed."}
        sorted_errors = sorted(error_count.items(), key=lambda x: x[1], reverse=True)
        suggestions = {
            "frequent_error_categories": sorted_errors,
            "suggestion": "Focus on resolving errors in the most frequent categories above."
        }
        return suggestions

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()