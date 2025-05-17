import os, json
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction=role,
        )

    def generate_response(self, prompt):
        print(f"📝 Prompt sent to {self.name}:\n{prompt[:500]}...")
        response = self.model.generate_content(prompt)
        print(f"🧾 Raw response from {self.name}:\n{response.text[:500]}...")
        return response.text.strip()
