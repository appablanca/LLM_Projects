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
 "financial_summary": {
  "2025-03": {
    "monthly_income_calculated_by_transaction": 10000,
    "total_spending_calculated_by_transaction": -9500,
    "net_difference_calculated_by_transaction": 500,
    "summary_comment": "You are saving money this month."
  },
  "2025-04": {
    ...
  }
}
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
    "On 08.03.2025, 03.02.2025 (You should mention all transaction dates of this spending if it occured more than once), you spent 181.95 TL on a taxi. Consider using public transport to save money."
  ],
  "Transaction_references": [
    " transaction_id_1",
    " transaction_id_6",]
    
  "financial_health": {
    "status": "Good",
    "percentage_of_financial_health": 80,
    "recommendation": "Continue to monitor your spending and adjust as necessary."
  }
}   
  '''json
    - The response should be in JSON format.
    
  
    Important Notes:
    - Do not mention any transaction that happens only once in the improvement suggestions .
    - Do not mention any suggestion without a specific date and amount in the improvement suggestions.
    - Do not mention any suggestion , if the transaction amount is too low (e.g. less than 100 TL).
    -Your suggestions should be personalized and grounded in the user's actual transactions and must be at least 7 suggestions.
    - The user data is provided in the input.
    - When giving suggestions, consider the user's financial situation and and mostly transactions and provide realistic options and give specific suggestions, examples.
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
        from collections import defaultdict
        from datetime import datetime

        def parse_amount(amt_str):
            try:
                amt_str = re.sub(r"[^\d,.-]", "", amt_str)
                if ',' in amt_str and '.' in amt_str:
                    amt_str = amt_str.replace('.', '')
                amt_str = amt_str.replace(',', '.')
                return float(amt_str)
            except Exception as e:
                print(f"parse_amount error for '{amt_str}': {e}")
                return 0.0

        monthly_data = defaultdict(lambda: {"income": 0.0, "spending": 0.0})

        for txn in transactions:
            amt = parse_amount(txn.get("amount", "0"))
            flow = txn.get("flow", "").lower()
            date_str = txn.get("date", "")
            try:
                try:
                    txn_date = datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    txn_date = datetime.strptime(date_str, "%d.%m.%Y")
                month_key = txn_date.strftime("%Y-%m")
            except Exception as e:
                print(f"Invalid date format '{date_str}': {e}")
                month_key = "unknown"

            if flow == "income":
                monthly_data[month_key]["income"] += amt
            elif flow == "spending":
                monthly_data[month_key]["spending"] += amt

        # Round results
        for key in monthly_data:
            monthly_data[key]["income"] = round(monthly_data[key]["income"], 2)
            monthly_data[key]["spending"] = round(monthly_data[key]["spending"], 2)

        return dict(monthly_data)

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
        
        def convert_objectid(obj):
            if isinstance(obj, list):
                return [convert_objectid(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: convert_objectid(v) for k, v in obj.items()}
            elif isinstance(obj, ObjectId):
                return str(obj)
            else:
                return obj

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
            convertedResult=convert_objectid(list(results))  # Convert ObjectId to string
            # embeddings alanını çıkar ve tüm ObjectId, date gibi alanları stringe çevir
            cleaned_results = [
            {k: v for k, v in doc.items() if k != "embeddings"}
            for doc in convertedResult
        ]

            print(f"{cleaned_results} for keyword '{keyword}' retrieved.")
            all_results.extend(cleaned_results)

            return all_results

    
    

    
    def filter_transactions(self, transactions, min_amount=0.0, max_per_category=5):
        def parse_amount(amt_str):
            a = re.sub(r"[^\d,.-]", "", amt_str).replace(",", ".")
            try:
                return float(amt_str)
            except:
                return 0.0

        filtered = {}
        for txn in transactions:
            amt = parse_amount(txn.get("amount", "0"))
            if amt < min_amount:
                continue
            cat = txn.get("spendingCategory", "unknown")
            if cat not in filtered:
                filtered[cat] = []
            if len(filtered[cat]) < max_per_category:
                filtered[cat].append(txn)
        # flatten list
        return [item for sublist in filtered.values() for item in sublist]
    
    
    def run_budget_analysis(self, user_id):

        
        userInfo = self.get_user_data(user_id)
        if not userInfo:
            print("❌ No data retrieved for user.")
            return None


        spending_data = userInfo["spending_data"]
        transactions = spending_data["data"]["transactions"]

        if not transactions:
            print("⚠️ No transactions found!")

        # Gelir ve harcamaları ay ay hesapla
        monthly_data = self.calculate_income_and_spending(transactions)

        monthly_summaries = {}
        for month, data in monthly_data.items():
            income = data.get("income", 0.0)
            spending = data.get("spending", 0.0)
            net_difference = round(income - spending, 2)
            summary_comment = (
                "Your monthly budget is in deficit."
                if net_difference < 0
                else "You are saving money this month."
            )
            monthly_summaries[month] = {
                "monthly_income_calculated_by_transaction": income,
                "total_spending_calculated_by_transaction": spending,
                "net_difference_calculated_by_transaction": net_difference,
                "summary_comment": summary_comment,
            }

        # En güncel ayı ana financial_summary olarak set et
        latest_month = sorted(monthly_summaries.keys())[-1] if monthly_summaries else "unknown"
        userInfo["user_info"]["income"] = monthly_summaries.get(latest_month, {}).get("monthly_income_calculated_by_transaction", 0.0)
        userInfo["financial_summary"] = monthly_summaries
        userInfo["categoryTotals"] = userInfo["spending_data"]["data"].get("categoryTotals", {})

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
  
        print(f"📥Before filtering retrieved {len(relevant_txns)} relevant transactions from vector DB")

        # relevant_txns = self.filter_transactions(relevant_txns)

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
            
            return json.loads(response.text.strip())
        except Exception as e:
            print("❌ LLM error:", e)
            return {"error": "LLM failed to return valid JSON."}
