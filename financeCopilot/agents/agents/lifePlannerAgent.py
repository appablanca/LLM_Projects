from agents.baseAgent import Agent        
import os
import httpx
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

app = FastAPI()

lifePlannerAgentRole = """
You are a smart financial assistant helping users build a personal life plan.

Your responsibilities:
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

    async def fetch_user_data(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BACKEND_URL}/userPanel/getFields?userId=6818ee0c6507de8196c00a55")
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

    async def get_life_plan(self, user_message):
        try:
            user_data = await self.fetch_user_data()
            macro_data = await self.fetch_macro_data()
            parsed_profile = await self.parse_user_fields(user_data)

            formatted_profile = f"""
Kullanıcı profili:
- Yaş: {parsed_profile.get("age")}
- Şehir: {parsed_profile.get("city")}
- Gelir: {parsed_profile.get("income")} TL/ay
- Kira: {parsed_profile.get("rent")} TL/ay
- Birikim: {parsed_profile.get("savings")} TL
- Medeni Durum: {parsed_profile.get("marital_status")}
- Çocuk: {parsed_profile.get("children")}
- Risk Toleransı: {parsed_profile.get("risk_tolerance")}
"""

            inflation = macro_data.get("inflationRate", "Bilinmiyor")
            usd_to_try = macro_data.get("usdToTry", "Bilinmiyor")
            car_price_index = macro_data.get("carPriceIndex", "Bilinmiyor")
            housing_price_index = macro_data.get("housingPriceIndex", "Bilinmiyor")

            macro_info = f"""
            Güncel ekonomik göstergeler:
            - Enflasyon oranı: {inflation}%
            - USD/TRY kuru: {usd_to_try}
            - Araç fiyat endeksi: {car_price_index}
            - Konut fiyat endeksi: {housing_price_index}
            """

            prompt = f"""
{user_message}
Lütfen aşağıdaki kullanıcı profilini ve ekonomik göstergeleri kullanarak detaylı, zamana yayılmış, gerçekçi bir hayat planı oluştur.
{formatted_profile}
{macro_info}
"""

            print(f"📎 Prompt sent to model:\n{prompt}")

            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip())

        except Exception as e:
            print(f"Error in get_life_plan: {e}")
            return json.dumps({"error": "Hayat planı oluşturulamadı."})