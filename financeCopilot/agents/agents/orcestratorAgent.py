
import json
import google.generativeai as genai

from agents.baseAgent import Agent

from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole
from agents.investmentAdvisorAgent import InvestmentAdvisorAgent, investmentAdvisorAgentRole


orcestratorAgentRole = f"""
You have TWO distinct responsibilities. Decide which one to perform based on the input:

1. **Job: "routing"**
   - Analyze the user's message and full conversation history.
   - Determine which of the following agents is best suited to handle the request.
   - Return a structured JSON response with:
     {{
       "job": "routing",
       "selected_agent": "<one of: lifeplanneragent | expenseanalyzeragent | normalchatagent | investmentadvisoragent>",
       "agent_response": null
     }}

2. **Job: "transporting"**
   - You are given the user's original message and the output from the selected agent.
   - Your task is to not change the agent's structured or technical reponse and to give the same exact output.
   - Return a structured JSON response with:
     {{
       "job": "transporting",
       "selected_agent": null,
       "agent_response": "<the agent's structured or technical response>"
       "URLs": ["<optional list of URLs to reference>"]
     }}

Agents and their roles:
- lifePlannerAgent: {lifePlannerAgentRole}
- expenseAnalyzerAgent: {expenseAnalyzerRole}
- normalChatAgent: {normalChatAgentRole}
- investmentAdvisorAgent: {investmentAdvisorAgentRole}

CRITICAL RULES:
- You must return exactly one of the two job types: "routing" or "transporting"
- The output must always follow the structure:
  {{
    "job": "...",
    "selected_agent": "...", // filled only if job is "routing"
    "agent_response": "..." // filled only if job is "transporting"
  }}
  
- You must infer intent from the current message and past context if available.
- If the last agent's message ended with a question, return the same agent under the "routing" job.
- Always use the same language as the user's input.

You are a highly capable orchestrator.
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

            response = self.model.generate_content(agent_output)
            print(response.text.strip())
            return response.text.strip()

        except Exception as e:
            print(f"🚨 Error generating final response: {e}")
            return "Sorry, I had trouble generating a final response."


