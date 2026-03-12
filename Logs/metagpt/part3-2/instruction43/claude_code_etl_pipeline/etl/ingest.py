import os
import json
import requests
from typing import List, Dict, Any, Optional, Union
from loguru import logger


class Ingestor:
    """
    Ingestor class for fetching raw Claude Code conversation data from a source.
    Supported sources: local file (JSONL), HTTP API endpoint, or message queue (future extension).
    """

    def __init__(self, source: str):
        """
        Initialize the Ingestor.

        Args:
            source (str): Path to file or URL of API endpoint.
        """
        self.source = source
        self.source_type = self._detect_source_type(source)
        logger.info(f"Ingestor initialized with source: {source} (type: {self.source_type})")

    def _detect_source_type(self, source: str) -> str:
        """
        Detect the type of source: 'file', 'api', or 'unknown'.

        Args:
            source (str): Source string.

        Returns:
            str: Source type.
        """
        if source.startswith("http://") or source.startswith("https://"):
            return "api"
        elif os.path.isfile(source):
            return "file"
        else:
            return "unknown"

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch raw Claude Code conversation data from the source.

        Returns:
            List[Dict[str, Any]]: List of raw conversation records.

        Raises:
            RuntimeError: If source type is unsupported or fetch fails.
        """
        logger.info(f"Fetching data from source: {self.source} (type: {self.source_type})")
        if self.source_type == "file":
            return self._fetch_from_file(self.source)
        elif self.source_type == "api":
            return self._fetch_from_api(self.source)
        else:
            logger.error(f"Unsupported source type: {self.source_type}")
            raise RuntimeError(f"Unsupported source type: {self.source_type}")

    def _fetch_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Fetch data from a local file (expects JSONL format).

        Args:
            file_path (str): Path to the file.

        Returns:
            List[Dict[str, Any]]: List of raw conversation records.
        """
        records = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping invalid JSON line: {e}")
            logger.info(f"Fetched {len(records)} records from file: {file_path}")
            return records
        except Exception as e:
            logger.error(f"Failed to fetch from file: {e}")
            raise

    def _fetch_from_api(self, api_url: str) -> List[Dict[str, Any]]:
        """
        Fetch data from an HTTP API endpoint.

        Args:
            api_url (str): API endpoint URL.

        Returns:
            List[Dict[str, Any]]: List of raw conversation records.
        """
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                logger.info(f"Fetched {len(data)} records from API: {api_url}")
                return data
            elif isinstance(data, dict) and "records" in data and isinstance(data["records"], list):
                logger.info(f"Fetched {len(data['records'])} records from API: {api_url}")
                return data["records"]
            else:
                logger.error("API response format is invalid. Expected list or dict with 'records'.")
                raise RuntimeError("API response format is invalid. Expected list or dict with 'records'.")
        except Exception as e:
            logger.error(f"Failed to fetch from API: {e}")
            raise

# Example usage:
# ingestor = Ingestor("data/conversations.jsonl")
# raw_records = ingestor.fetch()