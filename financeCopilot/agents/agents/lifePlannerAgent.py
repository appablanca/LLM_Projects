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

lifePlannerAgentRole = """
You are a smart financial assistant helping users build a personal life plan.

Your responsibilities:
•⁠  Review the user's profile and the current conversation.
•⁠  If the topic affects the user's financial life, switch to 'life plan mode'.
•⁠  If not financially relevant, reply normally but still return JSON.
•⁠  Generate a structured life plan ONLY for the specific topic the user is talking about (e.g., only car plan if they're asking about a car).
•⁠  NEVER include investment advice or investment planning under any circumstances.
•⁠  If you need more details for a better plan, respond by asking a follow-up question.

# Output Rules:
•⁠  ALWAYS return a valid JSON.
•⁠  NEVER return plain text or markdown.
•⁠  DO NOT include unrelated sections.

## Expected JSON response format:

### When asking for more details:
{
  "askingQuestion": true,
  "question": "..."  // follow-up question in user's language
}

### When generating a life plan:
{
  "askingQuestion": false,
  "lifePlan": {
    "goal": "string",            // e.g. Buy a car
    "estimatedCost": "string",   // e.g. 500000 TRY
    "timeline": "string",        // e.g. 2 years
    "monthlyPlan": "string",     // e.g. Save 5000 TRY/month
    "additionalNotes": "string"  // optional tips or warnings
  }
}

# Language:
•⁠  Use the same language as the user.
"""


class LifePlannerAgent(Agent):
    def _init_(self, name, role):
        super()._init_(name, role)

    async def fetch_user_data(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BACKEND_URL}/userPanel/getFields?userId=6818ee0c6507de8196c00a55")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching user data: {e}")
                return {}


    async def get_life_plan(self, user_message):
      try:
        user_data = await self.fetch_user_data()
        print(f"📎 User data: {user_data}")

        response = self.model.generate_content(user_message + "User profile: " + json.dumps(user_data))
        return json.loads(response.text.strip())

      except Exception as e:
        print(f"Error in get_life_plan: {e}")
        return json.dumps({"error": "Hayat planı oluşturulamadı."})