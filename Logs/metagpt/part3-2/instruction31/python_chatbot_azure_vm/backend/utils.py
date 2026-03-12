import os
import aiohttp

class OpenAIClient:
    """
    Handles communication with the OpenAI API.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key must be provided.")
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"  # You may change this to another model if needed

    async def generate_response(self, prompt: str) -> str:
        """
        Sends a prompt to the OpenAI API and returns the response text.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 256,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    error_detail = await resp.text()
                    raise Exception(f"OpenAI API error: {resp.status} {error_detail}")
                data = await resp.json()
                # Extract the response from the API
                try:
                    return data["choices"][0]["message"]["content"].strip()
                except (KeyError, IndexError):
                    raise Exception("Malformed response from OpenAI API.")