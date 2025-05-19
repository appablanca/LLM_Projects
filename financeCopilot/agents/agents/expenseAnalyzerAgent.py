import os, json
import pdfplumber
import tempfile
from agents.baseAgent import Agent
import google.generativeai as genai
spendingCategories = [
    "food_drinks", "clothing_cosmetics", "subscription", "groceries",
    "transportation", "entertainment", "stationery_books", "technology",
    "bill_payment", "education", "health", "cash_withdrawal", "other"
]

expenseAnalyzerRole = f"""
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
11. Don't forget that such as -100,00 TL is negative amount ant it should be treated like expense/spending/payment.
12. All "amount" fields must be positive values. Do not include any minus signs.
13. Add a new field to each transaction named "flow". Use "spending" if the transaction is an expense (originally negative amount), or "income" if it is a refund or incoming money (originally positive).

Examples of such operations to exclude:
- Point usage:
  - "MaxiPuan Used"
  - "KULLANILAN PUAN"
  - "PUAN USED"
  - "REWARD POINT REDEEMED"
  - "-80,45 TL" with reference to point usage
- Point top-ups:
  - "%50 PUAN YÜKLEME"
  - "MAXIMUM GENÇ MARKET PUAN"
  - "BONUS YÜKLEME"
  - "PUAN YÜKLEME"
  - "REWARD POINT ADDED"
  - Any transaction that indicates loading or redeeming points instead of spending money.

**Important**: These are not real spending and should be skipped entirely.

14. For normal purchase transactions that **mention earned reward points**, such as:
  - "KAZANILANMAXİPUAN: 0,02"
  - "EARNED REWARD POINTS: 0.05"
  - "KAZANILAN PUAN"
  - "BONUS KAZANIMI"

Include these transactions, but **remove any reward point references** from the `description` field.  
The description should only contain relevant and clean purchase information (e.g., store name, location, brand, etc.), **not reward metadata**.

Examples:
- "CHILLINCAFEANKARATR KAZANILANMAXİPUAN:0,02" → "CHILLIN CAFE ANKARA TR"
- "BIM A.S./U633/EMEK4 //ANKARATR KAZANILAN PUAN: 0.15" → "BIM A.S./U633/EMEK4 //ANKARA TR"

15. Exclude transactions that represent **money transfers** or account operations — these are not actual spending.

Examples of such transactions to exclude:
- Any description that includes:
  - "HESAPTAN AKTARIM"
  - "TRANSFER"
  - "HAVALE"
  - "EFT"
  - "FAST"
  - "PARA AKTARIMI"
  - "MONEY MOVEMENT"
- These are internal account actions and should **not** be included in the `transactions` list.


Allowed spending categories: {spendingCategories}

Example Target JSON Structure:
{{
  "type": "receipt/invoice/account statement",
  "customer_info": {{
    "full_name": "Name Surname",
  }},
  "transactions": [
    {{
      "date": "DD/MM/YYYY",
      "spending_category": "groceries",
      "description": "Place Name City Country",
      "amount": "-1.000,00 TL",
      "flow": "spending"
    }},
    {{
      "date": "DD/MM/YYYY",
      "spending_category": "groceries",
      "description": "Place Name City Country",
      "amount": "1.000,00 TL",
      "flow": "income" 
    }}
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

"""

class ExpenseAnalyzerAgent(Agent):
    def __init__(self):
        super().__init__(name="Budget Planner Agent", role=expenseAnalyzerRole)
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

    """
    Extracts all text from the given PDF file using pdfplumber.
    Iterates through pages and combines the text into a single string.
    Returns the full text or raises an exception if extraction fails.
    """
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        print(f"🔍 Extracting text from: {pdf_path}")
        all_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    print(f"📄 Page {page_num + 1} text length: {len(text) if text else 0}")
                    if text:
                        all_text += text + "\n"
            print(f"✅ Total extracted text length: {len(all_text)}")
            print("📝 First 500 characters of extracted text:")
            print(all_text[:500])
            return all_text
        except Exception as e:
            print(f"❌ Error extracting text: {str(e)}")
            raise

    """
    Splits long text into smaller chunks without breaking lines.
    Each chunk stays under the specified max character limit.
    Useful for sending parts of the text to an LLM.
    """
    def split_text_into_chunks(self, text, max_chars=5000):
        chunks = []
        current = ""
        for line in text.splitlines():
            if len(current) + len(line) < max_chars:
                current += line + "\n"
            else:
                chunks.append(current.strip())
                current = line + "\n"
        if current.strip():
            chunks.append(current.strip())
        print(f"📦 Split text into {len(chunks)} chunks")
        print(f"📝 First chunk preview: {chunks[0][:200] if chunks else 'No chunks'}")
        return chunks


    """
    Analyzes the given PDF, extracts and parses its content.
    Sends chunks of text to an LLM and collects structured JSON output.
    Calculates spending totals and returns the final structured result.
    """
    def categorize_pdf(self, pdf_file) -> dict:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, pdf_file.filename)
        try:
            pdf_file.save(temp_path)
            print(f"📥 Loading PDF: {temp_path}")

            text = self.extract_text_from_pdf(temp_path)
            if not text.strip():
                raise ValueError("PDF boş ya da metin çıkarılamadı.")

            with open("extracted_text_debug.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print("✅ Saved extracted text to extracted_text_debug.txt")

            chunks = self.split_text_into_chunks(text, max_chars=5000)
            print(f"🔍 Split into {len(chunks)} chunks")

            all_transactions = []
            first_card_limit = None
            first_customer_info = None

            for i, chunk in enumerate(chunks):
                print(f"🚀 Processing chunk {i + 1}/{len(chunks)}")
                print(f"📝 Chunk preview: {chunk[:200]}")
                response = self.generate_response("Şu metni dönüştür:\n" + chunk)

                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                    except Exception as e:
                        print("❌ JSON dönüşüm hatası:", e)
                        raise

                try:
                    print(f"🤖 Agent response: {json.dumps(response, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    print("❌ Agent response parse hatası:", e)
                    print("🔁 Gelen yanıt:\n", response)

                if isinstance(response, dict):
                    customer = response.get("customer_info", {})
                    card = response.get("card_limit", {})
                    if not first_customer_info and customer.get("full_name"):
                        first_customer_info = customer
                    if not first_card_limit and (card.get("total_card_limit") or card.get("remaining_card_limit")):
                        first_card_limit = card

                    transactions = response.get("transactions", [])
                    all_transactions.extend(transactions)

            for t in all_transactions:
                raw_amount = t.get("amount", "")
                try:
                    amount_number = float(
                        raw_amount.replace(".", "").replace(",", ".").replace(" TL", "").replace("-", "").strip()
                    )
                    t["amount"] = f"{amount_number:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
                except (ValueError, TypeError) as e:
                    print("❌ Amount formatlama hatası:", e)


            all_category_totals = {}
            for t in all_transactions:
                if t.get("flow") != "spending":
                    continue
                cat = t.get("spending_category")
                amount_str = t.get("amount", "0,00 TL")
                try:
                    val = float(amount_str.replace(".", "").replace(",", ".").replace(" TL", ""))
                    prev_val = float(all_category_totals.get(cat, "0,00 TL").replace(".", "").replace(",", ".").replace(" TL", ""))
                    total = val + prev_val
                    formatted = f"{total:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
                    all_category_totals[cat] = formatted
                except:
                    pass

            final_output = {
                "type": "account statement",
                "customer_info": first_customer_info or {"full_name": None},
                "card_limit": first_card_limit or {
                    "total_card_limit": None,
                    "remaining_card_limit": None
                },
                "category_totals": all_category_totals,
                "transactions": all_transactions
                }

            return final_output

        except Exception as e:
            print("🚫 Hata:", e)
            raise
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)