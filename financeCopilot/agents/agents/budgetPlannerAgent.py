import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

from agents.baseAgent import Agent
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Get backend endpoint from environment
BACKEND_URL = os.getenv("BACKEND_URL")


budgetPlannerAgentRole= """
    You are budgetPlannerAgent and your role is to analyze the user's financial data and provide insights on their spending habits.
    You will receive a summary of the user's income and spending, along with a breakdown of spending by category.
    
    #Instructions:
    - Analyze the provided financial data.
    - Identify categories where the user is overspending.
    - Suggest areas where the user can save money.
    - Provide a summary of the user's financial health.
    - Offer improvement suggestions.
    - Be concise and clear in your responses.
    - Use the provided data to support your analysis.
    - Avoid unnecessary jargon and technical terms.
    
    
    #Language:
    - Use only English.
    
    This is the expected json response format:
    '''json
    {
  "user_info": {
    "name": "John Doe",
    "age": 30,
    "location": "New York",
    "rent": 2000,
    "income": 12000,
    "savings": 5000
  },    
  "financial_summary": {
    "monthly_income": 12000 (You should calculate this from the user transcations),
    "total_spending": 13500,
    "net_difference": -1500,
    "summary_comment": "Your monthly budget is in deficit."
  },
  "spending_analysis": [
    {
      "category": "Groceries",
      "amount": 3200,
      "income_ratio_percent": 26.7,
      "comment": "Overspending in this category."
    }...
  ],
  "overspending_alerts": [
    {
      "category": "Groceries",
      "reason": "Spending exceeds 25% of your income.",
      "suggestion": "Plan your grocery list and take advantage of discounts."
    }...
  ],
  "saving_suggestions": [
    {
      "area": "Entertainment",
      "expected_saving": 1000,
      "suggestion": "Reduce entertainment spending to 10% of your income."
    }...
  ],
  "improvement_recommendations": [
    "Try to keep fixed expenses under 50% of your income."
  ]
  "financial_health": {
    "status": "Good",
    "percentage_of_financial_health": 80,
    "recommendation": "Continue to monitor your spending and adjust as necessary."
  }
}   
  '''json
    - The response should be in JSON format.
    
    #Note:
    - The user data is provided in the input.
    - When giving suggestions, consider the user's financial situation and provide realistic options and give specific suggestions, examples.
"""

class BudgetPlannerAgent(Agent):
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

    

    # Fetch user data from backend API
    def get_user_data(self,user_id):
        try:
            userSpendings = requests.get(f"{BACKEND_URL}/transactions/getTransactionsAndSpending?userId={user_id}")
            userInfo = requests.get(f"{BACKEND_URL}/userPanel/getFields?userId={user_id}")
            userSpendings.raise_for_status()
            userInfo.raise_for_status()
            spending_data = userSpendings.json()
            user_info_data = userInfo.json()
            records = {
                "user_info": user_info_data,
                "spending_data": spending_data
            } 
            return records
        except Exception as e:
            print(f"API error: {e}")
            return None

    def generate_prompt(self, userInfo):
        lines = []
        lines.append("== User Information ==\n")
        lines.append(json.dumps(userInfo, indent=2, ensure_ascii=False))
        return "\n".join(lines)

    # Main function
    def run_budget_analysis(self,user_id):
        userInfo = self.get_user_data(user_id)
        if not userInfo:
            print("No data retrieved for user.")
            return None

        prompt = self.generate_prompt(userInfo)
        print("\n== Prompt Sent to Gemini ==\n")
        print(prompt)
        print("\n== Agent Response ==\n")
        response = self.model.generate_content(prompt)
        return json.loads(response.text.strip())
      
        