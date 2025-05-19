import json
from agents.baseAgent import Agent
import google.generativeai as genai
normalChatAgentRole = f"""
        You are a helpful assistant that answers general user questions.
        
        Your task:
        • Answer the user's questions in a friendly and informative manner.
        
        # Language:
        •⁠  Use the same language as the user.
        
        Respond ONLY in valid JSON.
        
            Example response:
            '''json
            {{
            "response": "Here is the information you requested."
            }}
            '''json

    """    
    
class NormalChatAgent(Agent):
    
    def __init__(self, name, role):
        super().__init__(name="Budget Planner Agent", role=normalChatAgentRole)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
            system_instruction=self.role,
        )

    def generate_response(self, prompt):
        response = self.model.generate_content(prompt)
        cleaned = response.text.strip().strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return response.text        



