import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiLLM:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def generate(self, prompt: str):
        """Generate response from Gemini"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",  # Updated model
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback if LLM fails
            return f"[LLM Error: {str(e)}]"