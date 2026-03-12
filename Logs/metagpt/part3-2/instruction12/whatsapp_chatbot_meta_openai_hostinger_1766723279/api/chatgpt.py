import os
import requests
from typing import Dict, Any, Optional

class ChatGPTAPI:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Calls OpenAI ChatGPT API with the given prompt and context.
        Returns the response text.
        """
        messages = []
        if context and "messages" in context:
            messages.extend(context["messages"])
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                return "Sorry, I couldn't generate a response at this time."
        except requests.RequestException as e:
            print(f"Error calling OpenAI API: {e}")
            return "Sorry, I couldn't connect to the AI service."
        except Exception as e:
            print(f"Unexpected error in ChatGPTAPI: {e}")
            return "Sorry, something went wrong with the AI service."


# Example usage (for integration/testing, not for production):
if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY", "")
    chatgpt = ChatGPTAPI(api_key=api_key)
    prompt = "Hello, how can I help you today?"
    response = chatgpt.get_response(prompt)
    print("ChatGPT response:", response)