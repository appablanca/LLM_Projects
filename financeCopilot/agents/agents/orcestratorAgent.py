import json
from agents.baseAgent import Agent

from agents.lifePlannerAgent import LifePlannerAgent
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent




agents = {
    # "investmentAdvisorAgent": InvestmentAdvisorAgent("InvestmentAdvisor", "You give personalized investment advice."),
    # "lifePlannerAgent": LifePlannerAgent("SurveyTaggerAgent", "You extract and tag survey responses."),
    "expenseAnalyzerAgent": ExpenseAnalyzerAgent("ExpenseAnalyzerAgent", expenseAnalyzerRole),
    "normalChatAgent": NormalChatAgent("NormalChatAgent", "You are a helpful assistant that answers user messages."),
}   


class Orcestrator(Agent):
   
    def route_request(self, user_input,uploaded_pdf):
        print(f"🔁 Routing request: {user_input}")
        agent_key = self.generate_response(user_input)
        print(f"Orchectrator response: {agent_key}")
        if isinstance(agent_key, dict):
            agent_key = json.dumps(agent_key)
        agent_key = agent_key.strip().lower()
        print(f"🔑 Gemini suggested agent key: {agent_key}")
        print(f"📎 Uploaded file: {uploaded_pdf.name if uploaded_pdf else 'None'}")

        for key in agents.keys():
            if key.lower() in agent_key:
                print(f"Selected Agent: {key}")
                if key == "expenseAnalyzerAgent":
                    if uploaded_pdf:
                        return agents[key].categorize_pdf(uploaded_pdf)
                    else:
                        return "Lütfen analiz edilecek bir PDF yükleyin."
                else:
                    return agents[key].generate_response(user_input)

        print("⚠️ Unknown agent key:", agent_key)
        return agents["NormalChatAgent"].generate_response(user_input)
