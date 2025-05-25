from agents.baseAgent import Agent        
from agents.job_tracking import job_status
import os
import httpx

import requests
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
•⁠ The wanted plan is not financially posible and infeasble with user's information, mention it.

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

   Important Instructions:
    - Do NOT leave fields like 'goal', 'estimatedCost', 'timeline', or 'monthlyPlan' vague or generic.
    - Each field must be detailed, specific, and consistent with the user's income and macroeconomic data.
    - Use a realistic tone. Avoid generic phrases like “This plan helps you improve your finances.”
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
    def get_vehicle_options(self, make, model):
        try:
            response = requests.get(
                f"https://api.carsxe.com/specs?make={make}&model={model}",
                params={"key": os.getenv("CARSXE_API_KEY")}
            )
            response.raise_for_status()
            data = response.json()
            vehicles = [
                {
                    "make": car.get("make"),
                    "model": car.get("model"),
                    "year": car.get("year"),
                    "price": car.get("price")
                }
                for car in data.get("vehicles", []) if "price" in car
            ]
            return vehicles[:5]  # İlk 5 aracı döndür
        except Exception as e:
            print(f"CarsXE API error: {e}")
            return []


    def get_housing_options(self, location):
        try:
            response = requests.get(
                f"https://api.zillow.com/propertySearch?location={location}",
                headers={"Authorization": f"Bearer {os.getenv('ZILLOW_API_KEY')}"}
            )
            response.raise_for_status()
            data = response.json()
            properties = [
                {
                    "address": prop.get("address"),
                    "rentEstimate": prop.get("rentEstimate"),
                    "bedrooms": prop.get("bedrooms"),
                    "bathrooms": prop.get("bathrooms"),
                    "squareFeet": prop.get("livingArea")
                }
                for prop in data.get("properties", []) if prop.get("rentEstimate")
            ]
            return properties[:5]  # İlk 5 evi döndür
        except Exception as e:
            print(f"Zillow API error: {e}")
            return []
    

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
        job_status["static-track-id"].setdefault("steps", []).append("Detecting user language and preparing profile...")
        job_status["static-track-id"]["step"] = "Detecting user language and preparing profile..."
        try:
            sessionUser= json.loads(user)
            user_data = await self.fetch_user_data(sessionUser["id"])
            job_status["static-track-id"].setdefault("steps", []).append("Fetched user data. Parsing profile and macroeconomic indicators...")
            job_status["static-track-id"]["step"] = "Fetched user data. Parsing profile and macroeconomic indicators..."
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
            job_status["static-track-id"].setdefault("steps", []).append("Generating prompt for Gemini...")
            job_status["static-track-id"]["step"] = "Generating prompt for Gemini..."

            instruction = f"""The user's message is in **{user_language.upper()}**.
            Respond in the same language the user asked the question.Please use the profile and macroeconomic data below to generate a realistic, step-by-step, time-based financial life plan."""

        

            prompt = f"""
            {user_message}
            {instruction}
            {profile_template}
            {macro_info}
            """

            print(f"📎 Prompt sent to model:\n{prompt}")
            job_status["static-track-id"].setdefault("steps", []).append("Calling Agent to generate financial life plan...")
            job_status["static-track-id"]["step"] = "Calling Agent to generate financial life plan..."

            response = self.model.generate_content(prompt)

            parsed_response = json.loads(response.text.strip())
            job_status["static-track-id"].setdefault("steps", []).append("Gemini response received. Post-processing results...")
            job_status["static-track-id"]["step"] = "Gemini response received. Post-processing results..."

            goal = parsed_response.get("lifePlan", {}).get("goal", "").lower()

            if "araba" in goal or "car" in goal or "otomobil" in goal:
                vehicle_data = self.get_vehicle_options(make="Renault", model="Megane")  
                job_status["static-track-id"].setdefault("steps", []).append("Fetching vehicle suggestions...")
                job_status["static-track-id"]["step"] = "Fetching vehicle suggestions..."
                vehicle_section = "Örnek Araçlar:\n" + "\n".join(
                [f"- {v['year']} {v['make']} {v['model']}: {v['price']} TRY" for v in vehicle_data]
    )
                parsed_response["lifePlan"]["recommendations"].append(vehicle_section)

            elif "ev" in goal or "house" in goal or "konut" in goal:
                housing_data = self.get_housing_options(location=parsed_profile.get("city", "Istanbul"))
                job_status["static-track-id"].setdefault("steps", []).append("Fetching housing suggestions...")
                job_status["static-track-id"]["step"] = "Fetching housing suggestions..."
                housing_section = "Örnek Konutlar:\n" + "\n".join(
                [f"- {h['address']} – {h['squareFeet']} m² – {h['rentEstimate']} TRY/ay" for h in housing_data]
    )
                parsed_response["lifePlan"]["recommendations"].append(housing_section)

            job_status["static-track-id"].setdefault("steps", []).append("Construction complete.")
            job_status["static-track-id"]["step"] = "Construction complete."

            return parsed_response


        except Exception as e:
            print(f"Error in get_life_plan: {e}")
            job_status["static-track-id"].setdefault("steps", []).append("Error occurred during life plan generation.")
            job_status["static-track-id"]["step"] = "Error occurred during life plan generation."
            return json.dumps({"error": "Hayat planı oluşturulamadı."})