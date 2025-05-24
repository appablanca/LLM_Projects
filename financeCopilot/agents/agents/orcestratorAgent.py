
import json
import google.generativeai as genai

from agents.baseAgent import Agent

from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole
from agents.investmentAdvisorAgent import InvestmentAdvisorAgent, investmentAdvisorAgentRole


orcestratorAgentRole = f"""
You have ONLY TWO tasks:
1. Route the user's request to the most appropriate agent based on the user's input and the conversation history.
2. Generate a final response for the user based on the agent's output and the user's original question.

The agents are:
"lifeplanneragent"
"expenseanalyzeragent"
"normalchatagent"
"investmentadvisoragent"

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
    "lifeplanneragent": LifePlannerAgent("LifePlannerAgent", lifePlannerAgentRole),
    "expenseanalyzeragent": ExpenseAnalyzerAgent("ExpenseAnalyzerAgent", expenseAnalyzerRole),
    "normalchatagent": NormalChatAgent("NormalChatAgent", normalChatAgentRole),
    "investmentadvisoragent": InvestmentAdvisorAgent("InvestmentAdvisorAgent", investmentAdvisorAgentRole)
}


class Orcestrator(Agent):
    def __init__(self, name, role):
        super().__init__(name=name, role=role)
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
        self.conversation_history = []

    def build_contextual_prompt(self, user_input):
        prompt = "Below is a log of previous conversation steps:\n"
        for step in self.conversation_history[-5:]:
            prompt += f"User: {step['user_input']}\n"
            prompt += f"Agent: {step['agent_key']}\n"
            prompt += f"Response: {step['agent_response']}\n"
        prompt += f"\nNow the user says: {user_input}\n"
        prompt += "Which agent should handle this?"
        return prompt

    def get_agent_key(self, user_input):
        print(f"🔁 Routing request: {user_input}")

        if self.conversation_history:
            last_turn = self.conversation_history[-1]
            last_agent = last_turn["agent_key"]
            last_response = last_turn["agent_response"]
            if isinstance(last_response, str) and (last_response.strip().endswith("?") or "?" in last_response.split()[-3:]):
                print(f"↪️ Agent {last_agent} asked a question, routing reply back to it.")
                return last_agent
            elif isinstance(last_response, dict) and "response" in last_response:
                response_text = last_response["response"]
                if isinstance(response_text, str) and (response_text.strip().endswith("?") or "?" in response_text.split()[-3:]):
                    print(f"↪️ Agent {last_agent} asked a question, routing reply back to it.")
                    return last_agent

        contextual_prompt = self.build_contextual_prompt(user_input)
        response = self.model.generate_content(contextual_prompt)
        agent_key = response.text.strip().lower()
        print(f"🔑 Gemini suggested agent key: {agent_key}")

        valid_keys = ["lifeplanneragent", "expenseanalyzeragent", "normalchatagent", "investmentadvisoragent"]
        for key in valid_keys:
            if key in agent_key:
                return key

        return "normalchatagent"

    def generate_final_response(self, user_input, agent_response):
        try:
            # If it's a string containing JSON, try parsing it
            if isinstance(agent_response, str):
                try:
                    agent_response = json.loads(agent_response)
                except json.JSONDecodeError:
                    pass  # keep as is if not JSON string

            # Format the agent output nicely
            agent_output = json.dumps(agent_response, indent=2) if isinstance(agent_response, dict) else str(agent_response)

            prompt = (
                "Below is a summary of the agent's output followed by the user's original question. "
                "Provide a clear and helpful final message for the user.\n"
                f"User: {user_input}\n"
                f"Agent's structured output:\n{agent_output}\n"
                "Final natural language message to user:\n"
            )

            response = self.model.generate_content(prompt)
            print(response.text.strip())
            return response.text.strip()

        except Exception as e:
            print(f"🚨 Error generating final response: {e}")
            return "Sorry, I had trouble generating a final response."

