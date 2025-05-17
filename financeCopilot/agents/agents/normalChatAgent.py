import json
from agents.baseAgent import Agent

normalChatAgentRole = f"""
        You are a helpful assistant that answers general user questions.
        
        Your task:
        • Answer the user's questions in a friendly and informative manner.
        
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
        super().__init__(name, role)

    def generate_response(self, prompt):
        response = self.model.generate_content(prompt)
        cleaned = response.text.strip().strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return response.text        



