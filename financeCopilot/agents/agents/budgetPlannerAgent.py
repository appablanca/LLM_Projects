import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Get backend endpoint from environment
BACKEND_URL = os.getenv("BACKEND_URL")

# Convert amount string ("1.234,56 TL") to float
def parse_amount(amount_str):
    return float(amount_str.replace(".", "").replace(",", ".").replace(" TL", ""))

# Fetch user data from backend API
def get_user_data(user_id):
    try:
        response = requests.get(f"{BACKEND_URL}/transactions?userId={user_id}")
        response.raise_for_status()
        records = response.json()
    except Exception as e:
        print(f"API error: {e}")
        return 0.0, 0.0, {}

    income_total = 0.0
    spending_total = 0.0
    category_totals = defaultdict(float)

    for record in records:
        try:
            amount = parse_amount(record["amount"])
            date = datetime.strptime(record["date"], "%d.%m.%Y")
            flow = record["flow"]
            category = record.get("spendingCategory", "unknown")

            if flow == "income":
                income_total += amount
            elif flow == "spending":
                spending_total += amount
                category_totals[category] += amount
        except Exception as e:
            print(f"Data processing error: {e}")

    return income_total, spending_total, category_totals

# Build the prompt for Gemini
def generate_prompt(income, spending, category_totals):
    lines = [f"Total Income: {income:.2f} TL", f"Total Spending: {spending:.2f} TL", "", "Spending by Category:"]
    for category, total in category_totals.items():
        lines.append(f"- {category}: {total:.2f} TL")
    lines.append("")
    lines.append("Please analyze these transactions. Which categories show overspending? Where can the user save money? Give a summary of their financial health and improvement suggestions.")
    return "\n".join(lines)

# Ask Gemini for analysis
def ask_gemini(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Main function
def run_budget_analysis(user_id):
    income, spending, category_totals = get_user_data(user_id)
    if income == 0 and spending == 0:
        print("No data retrieved for user.")
        return

    prompt = generate_prompt(income, spending, category_totals)
    print("\n== Prompt Sent to Gemini ==\n")
    print(prompt)
    print("\n== Agent Response ==\n")
    result = ask_gemini(prompt)
    print(result)

# Example usage
if __name__ == "__main__":
    user_id = "6818ee0c6507de8196c00a55"
    run_budget_analysis(user_id)