import os
import json
import csv
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
import threading

class Storage:
    """
    Storage utilities for saving and loading persistent data such as logs, trades, and configuration.
    Supports JSON and CSV formats as needed.
    Thread-safe for concurrent access.
    """

    def __init__(self):
        self._lock = threading.Lock()

    def save_json(self, data: Union[Dict, List], path: str):
        """
        Save a dictionary or list to a JSON file.
        """
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_json(self, path: str) -> Union[Dict, List]:
        """
        Load a dictionary or list from a JSON file.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"JSON file not found: {path}")
        with self._lock:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    def save_csv(self, data: List[Dict[str, Any]], path: str, fieldnames: Optional[List[str]] = None):
        """
        Save a list of dictionaries to a CSV file.
        """
        if not data:
            raise ValueError("No data to save to CSV.")
        with self._lock:
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)

    def load_csv(self, path: str) -> List[Dict[str, Any]]:
        """
        Load a list of dictionaries from a CSV file.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV file not found: {path}")
        with self._lock:
            with open(path, "r", newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [row for row in reader]

    def save_model(self, model: BaseModel, path: str):
        """
        Save a pydantic model to a JSON file.
        """
        self.save_json(model.dict(), path)

    def load_model(self, model_class: Any, path: str) -> BaseModel:
        """
        Load a pydantic model from a JSON file.
        """
        data = self.load_json(path)
        return model_class.parse_obj(data)

    def append_json(self, item: Dict, path: str):
        """
        Append a dictionary item to a JSON file containing a list.
        """
        with self._lock:
            if os.path.exists(path):
                data = self.load_json(path)
                if not isinstance(data, list):
                    raise ValueError("JSON file does not contain a list.")
            else:
                data = []
            data.append(item)
            self.save_json(data, path)

    def append_csv(self, item: Dict[str, Any], path: str, fieldnames: Optional[List[str]] = None):
        """
        Append a dictionary item to a CSV file.
        """
        with self._lock:
            file_exists = os.path.exists(path)
            if not fieldnames:
                fieldnames = list(item.keys())
            with open(path, "a", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(item)