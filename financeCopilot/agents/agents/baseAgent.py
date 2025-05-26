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
        chat = self.model.start_chat(history=[])
        self.chat=chat


    def generate_response(self, prompt):
        print(f"📝 Prompt sent to {self.name}:\n{prompt[:500]}...")
        response = self.model.generate_content(prompt)
        print(f"🧾 Raw response from {self.name}:\n{response.text[:500]}...")
        return response.text.strip()

    # ➕ Token bazlı maliyet hesaplama fonksiyonu
    @staticmethod
    def calculate_token_cost(input_tokens, output_tokens):
        cost_input = (input_tokens / 1_000_000) * 0.10
        cost_output = (output_tokens / 1_000_000) * 0.40
        total_cost = cost_input + cost_output
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost_usd": round(cost_input, 6),
            "output_cost_usd": round(cost_output, 6),
            "total_cost_usd": round(total_cost, 6),
        }

