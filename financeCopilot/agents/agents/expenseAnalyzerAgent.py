import os, json
import pdfplumber
from agents.baseAgent import Agent

spendingCategories = [
    "food_drinks", "clothing_cosmetics", "subscription", "groceries",
    "transportation", "entertainment", "stationery_books", "technology",
    "bill_payment", "education", "health", "cash_withdrawal", "other"
]

expenseAnalyzerRole = f"""
[... SAME LONG PROMPT OMITTED FOR BREVITY ...]
"""

class ExpenseAnalyzerAgent(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)

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

    def categorize_pdf(self, pdf_file) -> dict:
        temp_path = os.path.join('/tmp', pdf_file.filename)
        try:
            # Save the uploaded file temporarily
            pdf_file.save(temp_path)
            print(f"📥 Loading PDF: {temp_path}")

            text = self.extract_text_from_pdf(temp_path)
            print(f"📄 Extracted text length: {len(text)}")

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

                try:
                    print(f"🤖 Agent response: {json.dumps(response, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError as e:
                    print("❌ JSON parse hatası:", e)
                    print("🔁 Gelen yanıt:\n", response)
                    raise

                if isinstance(response, dict):
                    if i == 0:
                        first_customer_info = response.get("customer_info")
                        first_card_limit = response.get("card_limit")
                    transactions = response.get("transactions", [])
                    all_transactions.extend(transactions)

            for t in all_transactions:
                raw_amount = t.get("amount", "")
                try:
                    amount_number = float(
                        raw_amount.replace(".", "").replace(",", ".").replace(" TL", "").replace("-", "").strip()
                    )
                    flow_type = "income" if "-" not in raw_amount and not raw_amount.startswith("-") else "spending"
                    t["flow"] = flow_type
                    t["amount"] = f"{amount_number:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                    t["flow"] = "spending"

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
                "transactions": all_transactions,
                "card_limit": first_card_limit or {
                    "total_card_limit": None,
                    "remaining_card_limit": None
                },
                "category_totals": all_category_totals
            }

            return final_output

        except Exception as e:
            print("🚫 Hata:", e)
            raise
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)