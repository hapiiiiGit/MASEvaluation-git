import requests
from typing import List, Dict, Optional
import logging


class MachFormClient:
    """
    Client to fetch and parse data from MachForms.
    """

    def __init__(self, base_urls: Dict[str, str], api_keys: Dict[str, str], timeout: int = 10):
        """
        Initialize the MachFormClient.

        Args:
            base_urls (Dict[str, str]): Mapping of form_id to MachForm API endpoint URLs.
            api_keys (Dict[str, str]): Mapping of form_id to API keys for authentication.
            timeout (int): Timeout for HTTP requests in seconds.
        """
        self.base_urls = base_urls
        self.api_keys = api_keys
        self.timeout = timeout
        self.logger = logging.getLogger("MachFormClient")

    def fetch_form_data(self, form_id: str) -> List[Dict]:
        """
        Fetch and parse data from a MachForm.

        Args:
            form_id (str): The MachForm ID to fetch data from.

        Returns:
            List[Dict]: List of submission data dictionaries.
        """
        if form_id not in self.base_urls or form_id not in self.api_keys:
            self.logger.error(f"Form ID '{form_id}' not configured.")
            raise ValueError(f"Form ID '{form_id}' not configured.")

        url = self.base_urls[form_id]
        api_key = self.api_keys[form_id]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            submissions = self._parse_response(data)
            self.logger.info(f"Fetched {len(submissions)} submissions from form {form_id}.")
            return submissions
        except requests.RequestException as e:
            self.logger.error(f"Error fetching data from MachForm {form_id}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error parsing MachForm {form_id}: {e}")
            return []

    def _parse_response(self, data: dict) -> List[Dict]:
        """
        Parse the MachForm API response into a list of submission dicts.

        Args:
            data (dict): Raw response data from MachForm API.

        Returns:
            List[Dict]: List of parsed submissions.
        """
        # MachForm API responses may vary; adjust parsing as needed.
        # Assume 'entries' is the key for submissions.
        if "entries" in data and isinstance(data["entries"], list):
            return data["entries"]
        elif isinstance(data, list):
            return data
        else:
            # Try to find the first list in the response
            for v in data.values():
                if isinstance(v, list):
                    return v
        return []

    def fetch_all_forms(self, form_ids: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Fetch data from all configured MachForms or a subset.

        Args:
            form_ids (Optional[List[str]]): List of form IDs to fetch. If None, fetch all.

        Returns:
            Dict[str, List[Dict]]: Mapping of form_id to list of submissions.
        """
        results = {}
        ids = form_ids if form_ids is not None else list(self.base_urls.keys())
        for form_id in ids:
            results[form_id] = self.fetch_form_data(form_id)
        return results