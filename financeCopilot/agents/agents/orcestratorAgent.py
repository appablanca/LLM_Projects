import json
from agents.baseAgent import Agent

from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole
from agents.investmentAdvisorAgent import InvestmentAdvisorAgent, investmentAdvisorAgentRole


orcestratorAgentRole = f"""You are a simple router. Your ONLY job is to return ONE of these exact strings based on the user's request:
"lifeplanneragent"
"expenseanalyzeragent"
"normalchatagent"

Here are the agents and their roles:

- lifePlannerAgent: {lifePlannerAgentRole}
- expenseAnalyzerAgent: {expenseAnalyzerRole}
- normalChatAgent: {normalChatAgentRole}
- investmentAdvisorAgent: {investmentAdvisorAgentRole}

IMPORTANT RULES:
1. Return ONLY ONE of these exact strings: "lifeplanneragent", "expenseanalyzeragent", "investmentadvisoragent" ,"normalchatagent"
2. DO NOT add any other text, JSON, or formatting
3. DO NOT explain your choice
4. DO NOT ask questions
5. DO NOT include any other information
6. Just return the single word that best matches the user's request
7. You can see the previous conversation history, analyze it and decide which agent is the best fit for the user's request and current conversation.
8. If the last agent's response was a question, route the request back to that agent.
9. If the last agent's response was not a question, decide which agent is the best fit for the user's request and current conversation.  

# Language:
•⁠  Use the same language as the user.

"""

agents = {
    "lifePlannerAgent": LifePlannerAgent("LifePlannerAgent", lifePlannerAgentRole),
    "expenseAnalyzerAgent": ExpenseAnalyzerAgent("ExpenseAnalyzerAgent", expenseAnalyzerRole),
    "normalChatAgent": NormalChatAgent("NormalChatAgent", normalChatAgentRole),
    "investmentAdvisorAgent": InvestmentAdvisorAgent("InvestmentAdvisor", investmentAdvisorAgentRole)
}   


class Orcestrator(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)
        self.conversation_history = []
    
    def build_contextual_prompt(self, user_input):
        prompt = "Below is a log of previous conversation steps:\n"
        for step in self.conversation_history[-5:]:  # son 5 mesaj yeterli
            prompt += f"User: {step['user_input']}\n"
            prompt += f"Agent: {step['agent_key']}\n"
            prompt += f"Response: {step['agent_response']}\n"
        prompt += f"\nNow the user says: {user_input}\n"
        prompt += "Which agent should handle this?"

        return prompt
    
    def get_agent_key(self, user_input):
        print(f"🔁 Routing request: {user_input}")
        
        if self.conversation_log:
            last_turn = self.conversation_log[-1]
            last_agent = last_turn["agent_key"]
            last_response = last_turn["agent_response"]

            # Eğer son cevap bir soruyla bittiyse, devam etmek mantıklıdır
        if last_response.strip().endswith("?") or "?" in last_response.split()[-3:]:
                print(f"↪️ Agent {last_agent} asked a question, routing reply back to it.")
                return last_agent
        
        # Yoksa yeniden karar ver
        contextual_prompt = self.build_contextual_prompt(user_input)
        response = self.model.generate_content(contextual_prompt)
        agent_key = response.text.strip().lower()
        print(f"🔑 Gemini suggested agent key: {agent_key}")

        valid_keys = ["lifeplanneragent", "expenseanalyzeragent", "normalchatagent", "investmentadvisoragent"]
        for key in valid_keys:
            if key == agent_key:
                return key

        return "normalchatagent"

