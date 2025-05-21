import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json

from agents.baseAgent import Agent

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
BACKEND_URL = os.getenv("BACKEND_URL")

budgetPlannerAgentRole = """
You are budgetPlannerAgent and your role is to analyze the user's financial data and provide insights on their spending habits.
...
"""  # Rol tanımını aynı tutabilirsin

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

    def get_user_data(self, user_id):
        try:
            userSpendings = requests.get(
                f"{BACKEND_URL}/transactions/getTransactionsAndSpending?userId={user_id}")
            userInfo = requests.get(
                f"{BACKEND_URL}/userPanel/getFields?userId={user_id}")
            userSpendings.raise_for_status()
            userInfo.raise_for_status()

            spending_data = userSpendings.json()
            user_info_data_raw = userInfo.json()

            user_info_data = {
                field["name"]: field["content"] for field in user_info_data_raw if not field.get("deleted", False)
            }

            return {
                "user_info": user_info_data,
                "spending_data": spending_data
            }
        except Exception as e:
            print(f"API error: {e}")
            return None

    def calculate_income_and_spending(self, transactions):
        def parse_amount(amt_str):
            try:
                return float(amt_str.replace('.', '').replace(',', '.').replace(' TL', '').strip())
            except:
                return 0.0

        income = 0.0
        spending = 0.0
        for txn in transactions:
            amt = parse_amount(txn["amount"])
            if txn["flow"] == "income":
                income += amt
            elif txn["flow"] == "spending":
                spending += amt
        return round(income, 2), round(spending, 2)

    def generate_prompt(self, userInfo):
        lines = []
        lines.append("== User Financial Data ==\n")
        lines.append(json.dumps(userInfo, indent=2, ensure_ascii=False))
        return "\n".join(lines)

    def run_budget_analysis(self, user_id):
        userInfo = self.get_user_data(user_id)
        if not userInfo:
            print("No data retrieved for user.")
            return None

        spending_data = userInfo["spending_data"]
        transactions = spending_data["data"]["transactions"]

        # Gelir ve harcamaları hesapla
        income, spending = self.calculate_income_and_spending(transactions)
        net_difference = round(income - spending, 2)

        # Kullanıcı bilgilerini güncelle
        userInfo["user_info"]["income"] = income
        userInfo["financial_summary"] = {
            "monthly_income": income,
            "total_spending": spending,
            "net_difference": net_difference,
            "summary_comment": "Your monthly budget is in deficit." if net_difference < 0 else "You are saving money this month."
        }

        # === Yeni Improvement Recommendations Mantığı ===
        recommendations = []
        user_data = userInfo["user_info"]

        rent = float(user_data.get("rent", 0))
        savings = float(user_data.get("savings", 0))

        # Sabit gider kontrolü
        fixed_expense_ratio = (rent / income) * 100 if income else 0
        if fixed_expense_ratio > 50:
            recommendations.append(
                f"Your rent consumes {fixed_expense_ratio:.1f}% of your income. Consider finding more affordable housing or increasing income sources."
            )

        # Tasarruf kontrolü
        savings_ratio = (savings / income) * 100 if income else 0
        if savings_ratio < 10:
            recommendations.append(
                f"Your savings rate is only {savings_ratio:.1f}%. Aim to save at least 20% of your income by automating savings at the start of each month."
            )

        # Genel iyileştirme önerileri
        recommendations.append("Track all expenses using an app or a simple spreadsheet to better understand your spending habits.")
        recommendations.append("Review monthly subscriptions and cancel any unused or non-essential services.")
        recommendations.append("Set specific monthly limits for categories like dining out, entertainment, or shopping.")

        userInfo["improvement_recommendations"] = recommendations

        # LLM'e gönderilecek prompt
        prompt = self.generate_prompt(userInfo)
        print("\n== Prompt Sent to Gemini ==\n")
        print(prompt)
        print("\n== Agent Response ==\n")
        response = self.model.generate_content(prompt)

        # Dönüş
        return json.loads(response.text.strip())
