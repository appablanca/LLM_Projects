from agents.baseAgent import Agent        
import os
import httpx
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai
import json
from langdetect import detect

from dotenv import load_dotenv


load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

app = FastAPI()

lifePlannerAgentRole = """
You are a smart financial assistant helping users build a personal life plan.

Your responsibilities:
• Always respond in the same language the user asked the question.
•⁠  Always create a *realistic, **step-by-step, and **time-based* financial plan based on the user's goals.
•⁠  If the user’s goal is not currently possible (e.g., only 100 TRY savings), still create a future plan explaining:
    - How much they need to save
    - For how long
    - What kind of item (e.g., car, house) they can afford in the future
    - What alternatives they may consider
•⁠  Use macroeconomic data like inflation and price indices to make realistic estimations.
•⁠  Consider user’s income, expenses, and savings rate when calculating monthly plans.
•⁠  Always assume the user is serious and committed — help them succeed.
•⁠ The plan should always include a list of "recommendations":

•⁠  ⁠If it's about buying a car: suggest 2–3 sample car models in the entry or middle segment.
•⁠  ⁠If it's about buying a house: suggest 2–3 regions with city + neighborhood + m² information.
•⁠  ⁠If it's a child plan: suggest nanny/daycare support, parental leave, etc.
•⁠  ⁠If the topic is different, suggest sample steps or preferences that are also appropriate for the goal.

What to do:
•⁠  Review user profile and the topic.
•⁠  If the topic is financially relevant, generate a detailed life plan for that specific goal.
•⁠  If not financially relevant, reply normally but still return JSON.
•⁠ In the plans, provide a **percentage spending distribution** based on the user's income (for example: 30% rent, 20% savings, 10% transportation, etc.).
• Always respond in the same language the user asked the question.


•⁠ Consider the user's current spending habits when recommending this distribution.

•⁠ If the user is saving very little, explain what and how they can reduce it with percentage targets.

•⁠ Provide an explanation of this distribution in the Recommendations section:
- “You should spend 30% of your income on rent, currently it is 45%. Alternatively, living in neighborhood X will lower the rent rate.”
- “15% savings is recommended. You are currently saving 5%. If you save Y TL more per month, you will reach your goal in Z years.”

NEVER:
•⁠  Never reject a plan outright just because current savings are low.
•⁠  Never say only “yes” or “no”.
•⁠  Never include investment or financial product suggestions.

## Output JSON:

### If more info is needed:
{
  "askingQuestion": true,
  "question": "..." 
}

### If generating a life plan:
{
  "askingQuestion": false,
  "lifePlan": {
    "goal": "string",              
    "estimatedCost": "string",     
    "timeline": "string",          
    "monthlyPlan": "string",       
    "generalSummeryOfPlan": "string"
    "recommendations": ["string", "..."]
  }
}

•⁠  Plan should include inflation and current price data in calculations.
•⁠  Use user’s language (e.g. Turkish if the user is Turkish).
•⁠  Be clear and realistic.
"""

class LifePlannerAgent(Agent):
    def __init__(self, name, role):
        super().__init__(name="Budget Planner Agent", role=lifePlannerAgentRole)
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

    async def fetch_user_data(self,userId):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BACKEND_URL}/userPanel/getFields?userId={userId}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching user data: {e}")
                return {}

    async def fetch_macro_data(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "data.json")
            with open(file_path, "r", encoding="utf-8") as file:
                macro_data = json.load(file)
            return macro_data
        except Exception as e:
            print(f"Makro veriler okunamadı: {e}")
            return {
                "inflationRate": "Bilinmiyor",
                "usdToTry": "Bilinmiyor",
                "carPriceIndex": "Bilinmiyor",
                "housingPriceIndex": "Bilinmiyor"
            }

    async def parse_user_fields(self, fields):
        profile = {}
        for field in fields:
            key = field["name"].lower().replace(" ", "_")
            value = field["content"]
            profile[key] = value
        return profile        


    async def get_life_plan(self, user_message,user):
        user_language = detect(user_message)
        try:
            user_data = await self.fetch_user_data(user.id)
            macro_data = await self.fetch_macro_data()
            parsed_profile = await self.parse_user_fields(user_data)

        

        # 🔁 Makro verileri ayrı ayrı çek
            inflation = macro_data.get("inflationRate", "Bilinmiyor")
            usd_to_try = macro_data.get("usdToTry", "Bilinmiyor")
            car_price_index = macro_data.get("carPriceIndex", "Bilinmiyor")
            housing_price_index = macro_data.get("housingPriceIndex", "Bilinmiyor")

        # Profil ve makro verileri dize olarak hazırla
            
            profile_template = f"""
User Profile:
- Name: {parsed_profile.get("name", "")} {parsed_profile.get("surname", "")}
- Age: {parsed_profile.get("age")}
- Occupation: {parsed_profile.get("occupation")}
- City: {parsed_profile.get("city")}
- Income: {parsed_profile.get("income")} TRY/month
- Savings: {parsed_profile.get("savings")} TRY
- Housing: {parsed_profile.get("housing")}
- Rent: {parsed_profile.get("rent")}
- Marital Status: {parsed_profile.get("marital_status")}
- Children: {parsed_profile.get("children")}
- Financial Goals: {parsed_profile.get("financial_goals")}
- Investment Horizon: {parsed_profile.get("investment_horizon")}
- Investment Expectation: {parsed_profile.get("investment_expectation")}
- Income Use: {parsed_profile.get("income_use")}
- Loss Reaction: {parsed_profile.get("loss_reaction")}
- Retirement Plan: {parsed_profile.get("retirement_plan")}
- Risk Tolerance: {parsed_profile.get("risk_tolerance")}
- Investment Term: {parsed_profile.get("investment_term")}
"""


            macro_info = f"""
                Current Economic Indicators:
                - Inflation Rate: {inflation}%
                - USD/TRY Exchange Rate: {usd_to_try}
                - Car Price Index: {car_price_index}    
                - Housing Price Index: {housing_price_index}
                """

            instruction = f"""The user's message is in **{user_language.upper()}**.
            Respond in the same language the user asked the question.Please use the profile and macroeconomic data below to generate a realistic, step-by-step, time-based financial life plan."""

        

            prompt = f"""
            {user_message}
            {instruction}
            {profile_template}
            {macro_info}
            """
            # Prompt'a özel yüzdesel dağılım isteği ekle
            
            prompt += """
    Your response must be in the following JSON format and respond in the same language the user asked the question:

    {{
      "askingQuestion": false,
      "lifePlan": {{
        "goal": "string – Clearly state the user's objective (e.g., Buy a used C-segment car in 2 years)",
        "estimatedCost": "string – Estimate current cost in TRY (e.g., 900,000 – 1,100,000 TRY)",
        "timeline": "string – A realistic time-based path to achieve the goal (e.g., 'Start saving now, reach target by Q2 2026')",
        "monthlyPlan": "string – A clear, step-by-step financial plan including monthly or quarterly savings, spending adjustments, and key decisions",
        "generalSummeryOfPlan": "string – High-level summary of the approach and what the user will achieve by following it",
        "recommendations": ["string", "string", "..."]  // At least 5 detailed, realistic suggestions
      }}
    }}

    Important Instructions:
    - Do NOT leave fields like 'goal', 'estimatedCost', 'timeline', or 'monthlyPlan' vague or generic.
    - Each field must be detailed, specific, and consistent with the user's income and macroeconomic data.
    - Use a realistic tone. Avoid generic phrases like “This plan helps you improve your finances.”

    Example output:

    {{
      "askingQuestion": false,
      "lifePlan": {{
        "goal": "Buy a 2nd-hand C-segment car within 2 years",
        "estimatedCost": "1,000,000 – 1,200,000 TRY",
        "timeline": "24 months – save 30,000 TRY per month, adjust expenses, purchase in Q2 2026",
        "monthlyPlan": "Months 1–3: Reduce rent by moving to a cheaper area, saving 2,000 TRY/month. Months 4–12: Save 30,000 TRY/month while minimizing entertainment and transport costs. Month 13–24: Maintain same savings rate. At the end of 24 months, you will have approx. 1,000,000 TRY.",
        "generalSummeryOfPlan": "This plan focuses on disciplined savings and optimizing your current expenses to help you buy a mid-range car within 2 years.",
        "recommendations": [
          "Current rent is 7.69% of income (5,000 TRY). If needed, increase to 30% (up to 19,500 TRY) to improve living conditions.",
          "Savings target is 30,000 TRY/month. You are currently saving 20,000 TRY. Reduce transport and entertainment expenses to meet this target.",
          "Transportation: Switch from taxi to metro/bus to save up to 3,000 TRY/month.",
          "Consider buying models like Toyota Corolla (2021+), Renault Megane, or Fiat Egea with low mileage.",
          "Track spending weekly using a budgeting app to stay disciplined and adjust based on monthly surplus."
        ]
      }}
    }}
    """
            


            print(f"📎 Prompt sent to model:\n{prompt}")

            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip())

        except Exception as e:
            print(f"Error in get_life_plan: {e}")
            return json.dumps({"error": "Hayat planı oluşturulamadı."})
