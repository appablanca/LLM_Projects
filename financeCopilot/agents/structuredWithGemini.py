import os
import json
import google.generativeai as genai

def structure_text_to_json():
    messages = []

    GOOGLE_API_KEY = "AIzaSyC9Eh9t8QeLoPKI7d8Sw6x0qr4qVyT9QH4"
    genai.configure(api_key=GOOGLE_API_KEY)

    INPUT_FOLDER = "cikti_klasoru"
    OUTPUT_FOLDER = "structured_output"

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    txt_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
    if not txt_files:
        return ["Error: No .txt file found in the input folder."]

    input_path = os.path.join(INPUT_FOLDER, txt_files[0])

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    model = genai.GenerativeModel("gemini-2.0-flash")

    system_prompt = f"""
You are a text structuring assistant. Read the raw text below and format it according to the JSON schema provided.

Instructions:
1. Always include the fields: "type", "customer_info", "transactions", "card_limit", and "category_totals".
2. Keep all currency values exactly as they appear in Turkish Lira (TL), including commas and periods.
3. In the "transactions" list, format each item with the following fields in this exact order:
   - date
   - spending_category (must match one of the given categories)
   - description (clean and readable wording with proper spacing)
   - amount
4. Format descriptions by inserting appropriate spaces between merged words, brand names, and locations. For example:
   "MIGROSZIYAGOKALPANKARATR" should become "MIGROS ZIYA GOKALP ANKARA TR".
5. **Exclude any transactions related to reward points**. That means:
   - If a transaction includes words like "puan", "PUAN", or "MaxiPuan" in the description,
   - Do not include this transaction in the final JSON output.
6. In "card_limit", include only:
   - total_card_limit
   - remaining_card_limit
7. Categorize totals under the given list of categories based on transaction type.
8. Use null for any missing or unknown values.
9. Output must be valid, properly formatted JSON.
10. Exclude all transactions that are **point-related financial operations** — that is, when the transaction itself is a reward point usage or a point top-up. 
These transactions must be **excluded from the output** entirely.

Examples of such operations to exclude:
- Point usage:
  - “MaxiPuan Used”
  - “KULLANILAN PUAN”
  - “PUAN USED”
  - “REWARD POINT REDEEMED”
  - “-80,45 TL” with reference to point usage
- Point top-ups:
  - “%50 PUAN YÜKLEME”
  - “MAXIMUM GENÇ MARKET PUAN”
  - “BONUS YÜKLEME”
  - “PUAN YÜKLEME”
  - “REWARD POINT ADDED”
  - Any transaction that indicates loading or redeeming points instead of spending money.

**Important**: These are not real spending and should be skipped entirely.

11. For normal purchase transactions that **mention earned reward points**, such as:
  - “KAZANILANMAXİPUAN: 0,02”
  - “EARNED REWARD POINTS: 0.05”
  - “KAZANILAN PUAN”
  - “BONUS KAZANIMI”

Include these transactions, but **remove any reward point references** from the `description` field.  
The description should only contain relevant and clean purchase information (e.g., store name, location, brand, etc.), **not reward metadata**.

Examples:
- "CHILLINCAFEANKARATR KAZANILANMAXİPUAN:0,02" → "CHILLIN CAFE ANKARA TR"
- "BIM A.S./U633/EMEK4 //ANKARATR KAZANILAN PUAN: 0.15" → "BIM A.S./U633/EMEK4 //ANKARA TR"

12. Exclude transactions that represent **money transfers** or account operations — these are not actual spending.

Examples of such transactions to exclude:
- Any description that includes:
  - “HESAPTAN AKTARIM”
  - “TRANSFER”
  - “HAVALE”
  - “EFT”
  - “FAST”
  - “PARA AKTARIMI”
  - “MONEY MOVEMENT”
- These are internal account actions and should **not** be included in the `transactions` list.


Allowed spending categories:
[
  "food_drinks",
  "clothing_cosmetics",
  "subscription",
  "groceries",
  "transportation",
  "entertainment",
  "stationery_books",
  "technology",
  "bill_payment",
  "education",
  "health",
  "cash_withdrawal",
  "other"
]

Target JSON Structure:
{{
  "type": "receipt/invoice/account statement",
  "customer_info": {{
    "full_name": "MELİSA SUBAŞI"
  }},
  "transactions": [
    {{
      "date": "01.04.2024",
      "spending_category": "groceries",
      "description": "MIGROS ZIYA GOKALP ANKARA TR",
      "amount": "215,75 TL"
    }},
    ...
  ],
  "card_limit": {{
    "total_card_limit": "2.000,00 TL",
    "remaining_card_limit": "851,50 TL"
  }},
  "category_totals": {{
    "groceries": "1.012,50 TL",
    ...
  }}
}}

Convert this raw text:
{raw_text}
"""



    try:
        response = model.generate_content(system_prompt)

        # --- CLEANING ---
        raw_response = response.text.strip()

        # Markdown block varsa ayıkla
        if "```json" in raw_response:
            cleaned_text = raw_response.split("```json")[1].split("```")[0].strip()
        else:
            cleaned_text = raw_response.strip("`").strip()

        # Geçici yer tutucular ("..." gibi) varsa kaldır
        cleaned_text = cleaned_text.replace("...", "")

        # JSON PARSING
        try:
            json_data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            # Model çıktısını hata halinde kaydet
            raw_out_path = os.path.join(OUTPUT_FOLDER, "raw_model_output.txt")
            with open(raw_out_path, "w", encoding="utf-8") as f:
                f.write(raw_response)
            messages.append("JSON format error:")
            messages.append(str(e))
            messages.append(f"Raw model output saved to: {raw_out_path}")
            return messages

        # Save valid JSON
        output_path = os.path.join(OUTPUT_FOLDER, "output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        messages.append(f"✅ JSON file successfully saved to: {output_path}")

    except Exception as e:
        messages.append(f"❌ An unexpected error occurred: {e}")

    return messages

# Example usage
if __name__ == "__main__":
    results = structure_text_to_json()
    for msg in results:
        print(msg)