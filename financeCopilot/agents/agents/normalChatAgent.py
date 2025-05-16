import json
from agents.agents.baseAgent import Agent
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



