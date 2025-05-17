from agents.baseAgent import Agent        
import os
import httpx
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")


app = FastAPI()

lifePlannerAgentRole = f"""
        You are a smart financial assistant helping users build a personal life plan.

        Your task:
        •⁠  Review the user profile and the ongoing dialogue.
        •⁠  If you need more detail or believe it would improve the plan, ask a follow-up question.
        •⁠  If the data is sufficient, generate a full life plan.
        •⁠  You can use the user profile data to inform and specify your response.


        Respond ONLY in valid JSON.

            If asking another question:
         '''json   
        {{
        "askingQuestion": true,
        "question": "..."
        }}
        '''json

            If ready to generate the plan:
        '''json    
        {{
        "askingQuestion": false,
        "lifePlan": {{
            "carPlan": {{
            "savingPeriod": "...",
            "recommendedModel": "...",
            "averageCost": ...
            }},
            "housingPlan": {{
            "recommendedPurchaseTime": "...",
            "suggestedLocation": "...",
            "averageCost": ...,
            "downPayment": ...
            }},
            "investmentPlan": {{
            "monthlyAmount": ...,
            "recommendedInstruments": ["...", "..."]
            }},
            "childrenPlan": {{
            "educationFundSuggestion": "..."
            }},
            "retirementPlan": {{
            "targetAge": ...,
            "targetSavings": ...
            }}
        }}
        }}
        '''json

        #Language:
        - Use the same language as the user.
        
        #Notes:
        •⁠  Use your judgment: even if data seems complete, you may ask more to improve accuracy.
        •⁠  You can use the user profile data to inform your response.
        •⁠  Only include childrenPlan if applicable.
        •⁠  Do NOT return markdown or explanations. Only JSON.
    """
    

class LifePlannerAgent(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)
        
    async def fetch_user_data(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BACKEND_URL}/userPanel/getFields?userId=6818ee0c6507de8196c00a55")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching user data: {e}")
                return {} 

    async def get_life_plan(self, prompt):
        try:
            user_data = await self.fetch_user_data()
            print(f"📎 User data: {user_data}")
            response = self.model.generate_content(prompt + json.dumps(user_data))
            return response.text.strip()
        except Exception as e:
            print(f"Error in get_life_plan: {e}")
            return {"error": "Failed to generate life plan"}

