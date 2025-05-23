import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import json
from pymongo import MongoClient
import re
from bson import ObjectId

from agents.baseAgent import Agent

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
BACKEND_URL = os.getenv("BACKEND_URL")
MONGO_URL = os.getenv("MONGO_URL")

budgetPlannerAgentRole = """
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
  "financial_summary": { (This section is calculated by the system and given to you)
    "monthly_income_calculated_by_transaction": 12000 
    "total_spending_calculated_by_transaction": 13500,
    "net_difference_calculated_by_transaction": -1500,
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
    -Analyze the relevant transactions. When you give suggestion , if you notice excessive or frequent spending (e.g. taxis, food delivery, entertainment), highlight them with specific dates, amounts, and categories. Provide suggestions to reduce such expenses with alternatives. Example:
      "On 08/03/2025, you spent 181.95 TL on a taxi. Consider using public transport to save money."
      
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
        self.helperModel = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
        )
        self.mongo_client = MongoClient(MONGO_URL)
        self.transactions_collection = self.mongo_client["test"]["transactions" ]

    def get_user_data(self, user_id):
        try:
            userSpendings = requests.get(
                f"{BACKEND_URL}/transactions/getTransactionsAndSpending?userId={user_id}"
            )
            userInfo = requests.get(
                f"{BACKEND_URL}/userPanel/getFields?userId={user_id}"
            )
            userSpendings.raise_for_status()
            userInfo.raise_for_status()

            spending_data = userSpendings.json()
            user_info_data_raw = userInfo.json()

            user_info_data = {
                field["name"]: field["content"]
                for field in user_info_data_raw
                if not field.get("deleted", False)
            }

            return {"user_info": user_info_data, "spending_data": spending_data}
        except Exception as e:
            print(f"API error: {e}")
            return None

    def calculate_income_and_spending(self, transactions):
        # fonksiyon içinde ya da dosya başında olmalı
        def parse_amount(amt_str):
            try:
                # Sadece rakam, nokta, virgül, eksi işareti bırak
                amt_str = re.sub(r"[^\d,.-]", "", amt_str)
                # Noktaları kaldır (binlik ayırıcı), virgülü ondalık ayırıcı yap
                amt_str = amt_str.replace(".", "").replace(",", ".")
                return float(amt_str)
            except Exception as e:
                print(f"parse_amount error for '{amt_str}': {e}")
                return 0.0

        income = 0.0
        spending = 0.0

        for txn in transactions:
            amt = parse_amount(txn.get("amount", "0"))
            flow = txn.get("flow", "").lower()

            if flow == "income":
                income += amt
            elif flow == "spending":
                spending += amt

        return round(income, 2), round(spending, 2)

    def get_precomputed_embedding(self, text):
        try:
            response = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document",
            )
            return response["embedding"]
        except Exception as e:
            print(f"Embedding error: {e}")
            return []

    def initial_llm_analysis(self, user_info, financial_summary):
        prompt = f"""
      == User Info ==
      {json.dumps(user_info, indent=2)}

      == Financial Summary ==
      {json.dumps(financial_summary, indent=2)}

      Based on this data, what are the top 3 financial improvement areas to focus on? You can only return this keywords [
    "food_drinks", "clothing_cosmetics", "subscription", "groceries",
    "transportation", "entertainment", "stationery_books", "technology",
    "bill_payment", "education", "health", "cash_withdrawal", "other"
]
.
      """
        response = self.helperModel.generate_content(prompt)
        keywords = json.loads(response.text.strip())
        return keywords

    def retrieve_contextual_transactions(self, focus_keywords, top_k=80):
        all_results = []

        for keyword in focus_keywords:
            query_embedding = self.get_precomputed_embedding(keyword)
            print(f"🔍 Searching for keyword: {keyword}")

            results = self.transactions_collection.aggregate(
                [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "embeddings",
                            "queryVector": query_embedding,
                            "numDimensions": 768,
                            "numCandidates": 100,
                            "limit": top_k,
                        }
                    }
                ]
            )
            all_results.extend(list(results))
        return all_results

    def run_budget_analysis(self, user_id):

        def convert_objectid(obj):
            if isinstance(obj, list):
                return [convert_objectid(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: convert_objectid(v) for k, v in obj.items()}
            elif isinstance(obj, ObjectId):
                return str(obj)
            else:
                return obj

        userInfo = self.get_user_data(user_id)
        if not userInfo:
            print("❌ No data retrieved for user.")
            return None


        spending_data = userInfo["spending_data"]
        transactions = spending_data["data"]["transactions"]

        if not transactions:
            print("⚠️ No transactions found!")

        # Gelir ve harcamaları hesapla
        income, spending = self.calculate_income_and_spending(transactions)
        net_difference = round(income - spending, 2)

        userInfo["user_info"]["income"] = income
        userInfo["financial_summary"] = {
            "monthly_income_calculated_by_transcation": income,
            "total_spending_calculated_by_transaction": spending,
            "net_difference_calculated_by_transaction": net_difference,
            "summary_comment": (
                "Your monthly budget is in deficit."
                if net_difference < 0
                else "You are saving money this month."
            ),
        }

        print(
            "🧾 Financial Summary Computed:",
            json.dumps(userInfo["financial_summary"], indent=2),
        )

        # Anahtar kelimeleri bul
        focus_keywords = self.initial_llm_analysis(
            userInfo["user_info"], userInfo["financial_summary"]
        )
        print("🔎 LLM-suggested focus keywords:", focus_keywords)

        # Vektör araması ile ilgili işlemler
        relevant_txns = self.retrieve_contextual_transactions(
            focus_keywords
        )
        relevant_txns = convert_objectid(relevant_txns)
        # Remove 'embeddings' field from each transaction to reduce prompt size
        for txn in relevant_txns:
            txn.pop("embeddings", None)
        print(f"📥 Retrieved {len(relevant_txns)} relevant transactions from vector DB")
        if relevant_txns:
          print(f"Sample transaction: {relevant_txns[0]}")
        else:
          print("⚠️ No relevant transactions found.")

        # Prompt oluşturuluyor
        prompt = f"""
== User Info ==
{json.dumps(userInfo["user_info"], indent=2)}

== Financial Summary ==
{json.dumps(userInfo["financial_summary"], indent=2)}

== Relevant Transactions (via Vector Search) ==
{json.dumps(relevant_txns, indent=2)}

...
"""
        print("📝 Final Prompt Sent to LLM:\n", prompt[:1500], "...\n")
       
        try:
            response = self.model.generate_content(prompt)
            print("✅ Raw LLM Response:\n", response.text[:1500], "...\n")
            return json.loads(response.text.strip())
        except Exception as e:
            print("❌ LLM error:", e)
            return {"error": "LLM failed to return valid JSON."}
