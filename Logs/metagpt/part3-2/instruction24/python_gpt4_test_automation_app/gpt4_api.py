import requests
import json

class GPT4API:
    """
    Handles GPT-4 API integration for generating test input data.
    Provides generate_test_input(prompt: str) -> dict method.
    """

    def __init__(self, api_key: str, api_url: str = "https://api.openai.com/v1/chat/completions"):
        self.api_key = api_key
        self.api_url = api_url
        self.model = "gpt-4"  # You may change this if using a different model

    def generate_test_input(self, prompt: str) -> dict:
        """
        Sends a prompt to the GPT-4 API and returns the generated test input as a dictionary.
        The response is expected to be a JSON string representing the test input data.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates test input data for automated test scenarios in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 2048
        }

        response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            raise Exception(f"GPT-4 API request failed: {response.status_code} {response.text}")

        result = response.json()
        # Extract the content from the response
        try:
            content = result["choices"][0]["message"]["content"]
            # Try to parse the content as JSON
            test_input_data = json.loads(content)
            if not isinstance(test_input_data, dict):
                raise Exception("GPT-4 response is not a valid JSON object.")
            return test_input_data
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse GPT-4 response: {str(e)}")