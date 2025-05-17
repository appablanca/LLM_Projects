import json
from agents.baseAgent import Agent

from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole


orcestratorAgentRole = f"""You are a simple router. Your ONLY job is to return ONE of these exact strings based on the user's request:
"lifeplanneragent"
"expenseanalyzeragent"
"normalchatagent"

Here are the agents and their roles:

- lifePlannerAgent: {lifePlannerAgentRole}
- expenseAnalyzerAgent: {expenseAnalyzerRole}
- normalChatAgent: {normalChatAgentRole}

IMPORTANT RULES:
1. Return ONLY ONE of these exact strings: "lifeplanneragent", "expenseanalyzeragent", or "normalchatagent"
2. DO NOT add any other text, JSON, or formatting
3. DO NOT explain your choice
4. DO NOT ask questions
5. DO NOT include any other information
6. Just return the single word that best matches the user's request
"""

agents = {
    # "investmentAdvisorAgent": InvestmentAdvisorAgent("InvestmentAdvisor", "You give personalized investment advice."),
    "lifePlannerAgent": LifePlannerAgent("LifePlannerAgent", lifePlannerAgentRole),
    "expenseAnalyzerAgent": ExpenseAnalyzerAgent("ExpenseAnalyzerAgent", expenseAnalyzerRole),
    "normalChatAgent": NormalChatAgent("NormalChatAgent", normalChatAgentRole),
}   


class Orcestrator(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)
        
    def get_agent_key(self, user_input):
        print(f"🔁 Routing request: {user_input}")
        response = self.model.generate_content(user_input)
        agent_key = response.text.strip().lower()
        print(f"🔑 Gemini suggested agent key: {agent_key}")
        
        # Ensure we only return one of the valid agent keys
        valid_keys = ["lifeplanneragent", "expenseanalyzeragent", "normalchatagent"]
        for key in valid_keys:
            if key in agent_key:
                return key
                
        # If no valid key found, default to normalchatagent
        return "normalchatagent"

    def generate_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error in generate_response: {e}")
            return "I apologize, but I encountered an error processing your request."
