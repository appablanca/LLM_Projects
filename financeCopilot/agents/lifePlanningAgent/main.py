import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from generate_life_plan import generate_life_plan

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

app = FastAPI()

class GoalsUpdate(BaseModel):
    goals: list[str]

async def fetch_user_data(user_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_SERVICE_URL}?userId={user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Veri servisine erişilemedi: {str(e)}")

@app.get("/api/life-plan/{user_id}")
async def get_life_plan(user_id: str, ask_question: bool = False):
    user = await fetch_user_data(user_id)

    # Eksik veri kontrolü
    missing = []
    if not user.get("age"): missing.append("age")
    if not user.get("income"): missing.append("income")
    if not user.get("expenses"): missing.append("expenses")
    if not user.get("goals"): missing.append("goals")

    if missing:
        return {
            "error": "Eksik bilgi var",
            "missingFields": missing
        }

    result = await generate_life_plan(user, asking_question=ask_question)
    return result



