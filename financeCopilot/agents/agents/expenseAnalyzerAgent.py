import os, json
import pdfplumber
import tempfile
from agents.baseAgent import Agent
import google.generativeai as genai
from agents.job_tracking import job_status

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
   - flow
4. Format descriptions by inserting appropriate spaces between merged words, brand names, and locations.
   For example: "MIGROSZIYAGOKALPANKARATR" → "MIGROS ZIYA GOKALP ANKARA TR"
5. Exclude any transactions related to reward points:
   - If a transaction includes words like "puan", "PUAN", or "MaxiPuan" in the description,
   - Do not include it in the final JSON output.
6. In "card_limit", include only:
   - total_card_limit
   - remaining_card_limit
7. Categorize totals under the given list of categories based on transaction type.
8. Use null for any missing or unknown values.
9. Output must be valid, properly formatted JSON.
10. Exclude all transactions that are **point-related financial operations** (e.g. point usage or loading).
11. If a transaction amount is negative (e.g. -100,00 TL), it represents spending.
12. All "amount" fields must be positive values. Do not include any minus signs.
13. Add a field called "flow" to each transaction:
   - Use "spending" for originally negative amounts
   - Use "income" for originally positive amounts

Examples of operations to exclude:
- Point usage:
  - "MaxiPuan Used", "KULLANILAN PUAN", "REWARD POINT REDEEMED"
- Point top-ups:
  - "PUAN YÜKLEME", "REWARD POINT ADDED", "BONUS YÜKLEME", "%50 PUAN YÜKLEME"

These are not real spending and must be excluded.

14. For transactions that mention earned points:
  - e.g. "KAZANILANMAXİPUAN: 0,02" or "EARNED REWARD POINTS: 0.05"
  - Keep the transaction, but remove point references from the `description`.

Examples:
- "CHILLINCAFEANKARATR KAZANILANMAXİPUAN:0,02" → "CHILLIN CAFE ANKARA TR"
- "BIM A.S./U633/EMEK4 //ANKARATR KAZANILAN PUAN: 0.15" → "BIM A.S./U633/EMEK4 //ANKARA TR"

15. Exclude transactions that represent internal account operations or movement:
  - e.g. descriptions including: "HESAPTAN AKTARIM", "ACCOUNT MOVEMENT", "MONEY MOVEMENT"
  - These are not real spending or income.

16. Regarding income (incoming money) transactions:

  All transactions with a **positive amount** (e.g. +1.000,00 TL) must be included as `flow: "income"`.

  This includes:
  - Salaries: "MAAŞ", "Maaş Ödemesi"
  - Scholarships: "BURS", "BURSU"
  - Refunds: "İADE", "IYZICO", "TEMU", "RETURN", "REFUND", etc.
  - Deposits, incoming transfers: "FAST", "EFT", "TRANSFER", "HAVALE", "QR ILE PARA YATIRMA", etc.

  Even if the description contains "FAST", "TRANSFER", or similar keywords, 
  if the amount is positive, treat it as valid income.

  Do not exclude any transaction with a positive amount under any condition.

Examples of valid income:
- "MAAŞ ÖDEMESİ Maaş  +400,00 TL"
- "İLİM YAYMA CEMİYETİ BURS  +1.000,00 TL"
- "İADE -517040*7261-İYZİCO /S/TEMU  +321,78 TL"
- "FAST859190238-PELİN HAMDEMİR- Para Transferi  +500,00 TL"
- "CEP ŞUBE - HVL - EMİR BOZKURT  +5.000,00 TL"
- "QR ILE PARA YATIRMA-00082CRS003  +1.200,00 TL"

Allowed spending categories: {spendingCategories}

Example Target JSON Structure:
{{
  "type": "receipt/invoice/account statement",
  "customer_info": {{
    "full_name": "Name Surname"
  }},
  "transactions": [
    {{
      "date": "DD/MM/YYYY",
      "spending_category": "groceries",
      "description": "Place Name City Country",
      "amount": "1.000,00 TL",
      "flow": "income"
    }},
    {{
      "date": "DD/MM/YYYY",
      "spending_category": "groceries",
      "description": "Place Name City Country",
      "amount": "500,00 TL",
      "flow": "spending"
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

    def __init__(self, name, role):
        super().__init__(name=name, role=role)

        self.json_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            },
            system_instruction=self.role,
        )

        self.text_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 2048
            },
            system_instruction=self.role,
        )

# PDF'den metin çıkartır (tüm sayfaları birleştir)
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        print("📄 PDF'den metin çıkarılıyor...")
        all_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    print(f"📃 Sayfa {i}: {len(text) if text else 0} karakter")
                    if text:
                        all_text += text + "\n"
            print("✅ Metin çıkarma tamamlandı.")
            return all_text
        except Exception as e:
            print(f"❌ Metin çıkarma hatası: {str(e)}")
            raise

# Uzun metni parçalara böl (LLM token sınırı için)
    def split_text_into_chunks(self, text, max_chars=5000):
        print("✂️ Metin parçalara bölünüyor...")
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
        print(f"📦 {len(chunks)} adet parça oluşturuldu.")
        return chunks

# Ana fonksiyon bu:
        # - PDF'i geçici klasöre kaydet
        # - Metni çıkar, parçalara ayır
        # - Gemini ile her parçayı işle
        # - Tüm transaction'ları topla
        # - Miktarları normalize et
        # - Kategori toplamlarını hesapla
        # - Doğal dil özeti oluştur
        # - Final JSON'u döndür
    def categorize_pdf(self, pdf_file) -> dict:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, pdf_file.filename)

        try:
            print("📥 PDF dosyası geçici klasöre kaydediliyor...")
            pdf_file.save(temp_path)

            job_status["static-track-id"].setdefault("steps", []).append("Saving uploaded PDF to temporary directory...")
            job_status["static-track-id"]["step"] = "Saving uploaded PDF to temporary directory..."

            job_status["static-track-id"].setdefault("steps", []).append("Extracting text from PDF...")
            job_status["static-track-id"]["step"] = "Extracting text from PDF..."

            print(f"🗂️ Kaydedilen dosya: {temp_path}")

            text = self.extract_text_from_pdf(temp_path)

            job_status["static-track-id"].setdefault("steps", []).append("Splitting text into chunks for processing...")
            job_status["static-track-id"]["step"] = "Splitting text into chunks for processing..."

            if not text.strip():
                raise ValueError("📭 PDF boş veya metin içeremiyor.")

            chunks = self.split_text_into_chunks(text, max_chars=5000)

            job_status["static-track-id"].setdefault("steps", []).append("Sending chunks to Gemini for categorization...")
            job_status["static-track-id"]["step"] = "Sending chunks to Gemini for categorization..."

            all_transactions = []
            first_card_limit = None
            first_customer_info = None

            for i, chunk in enumerate(chunks):
                print(f"🤖 Gemini ile işleniyor: Parça {i+1}/{len(chunks)}")
                response = self.json_model.generate_content("Şu metni dönüştür:\n" + chunk)
                try:
                    parsed = json.loads(response.text)
                    print("✅ JSON verisi başarıyla çözüldü.")
                except Exception as e:
                    print(f"❌ JSON çözümleme hatası: {str(e)}")
                    continue

                customer = parsed.get("customer_info", {})
                card = parsed.get("card_limit", {})
                if not first_customer_info and customer.get("full_name"):
                    first_customer_info = customer
                if not first_card_limit and (card.get("total_card_limit") or card.get("remaining_card_limit")):
                    first_card_limit = card

                all_transactions.extend(parsed.get("transactions", []))

                job_status["static-track-id"].setdefault("steps", []).append(f"Chunk {i+1}/{len(chunks)} categorized.")
                job_status["static-track-id"]["step"] = f"Chunk {i+1}/{len(chunks)} categorized."

            print(f"💳 Toplam işlem sayısı: {len(all_transactions)}")

            job_status["static-track-id"].setdefault("steps", []).append("Normalizing amounts and calculating category totals...")
            job_status["static-track-id"]["step"] = "Normalizing amounts and calculating category totals..."

            for t in all_transactions:
                raw_amount = t.get("amount", "")
                try:
                    amount_number = float(
                        raw_amount.replace(".", "").replace(",", ".").replace(" TL", "").replace("-", "").strip()
                    )
                    t["amount"] = f"{amount_number:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
                except (ValueError, TypeError):
                    pass

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

            print("📊 Harcama kategorileri hesaplandı.")

            job_status["static-track-id"].setdefault("steps", []).append("Generating natural language summary...")
            job_status["static-track-id"]["step"] = "Generating natural language summary..."

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

            natural_summary = self.generate_natural_language_summary(final_output)
            final_output["natural_summary"] = natural_summary

            job_status["static-track-id"].setdefault("steps", []).append("Final output assembled. Analysis complete.")
            job_status["static-track-id"]["step"] = "Final output assembled. Analysis complete."

            print("🗣️ Doğal dil özeti eklendi.")

            print("✅ PDF analiz işlemi tamamlandı.")
            job_status["static-track-id"].setdefault("steps", []).append("Construction complete.")
            job_status["static-track-id"]["step"] = "Construction complete."      
            return final_output

        except Exception as e:
            job_status["static-track-id"].setdefault("steps", []).append("Error occurred during PDF analysis.")
            job_status["static-track-id"]["step"] = "Error occurred during PDF analysis."
            print("🚫 Genel hata:", e)
            raise
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print("🧹 Geçici dosya silindi.")

 # Kategorilere göre Türkçe doğal özet üretiyor
    def generate_natural_language_summary(self, final_output: dict) -> str:
        try:
            customer_name = final_output.get("customer_info", {}).get("full_name", "müşteri")
            category_totals = final_output.get("category_totals", {})

            if not category_totals:
                return "Harcama kategorisi bulunamadı."

            category_emojis = {
                "food_drinks": "🍽️",
                "clothing_cosmetics": "👗",
                "subscription": "📺",
                "groceries": "🛒",
                "transportation": "🚌",
                "entertainment": "🎭",
                "stationery_books": "📚",
                "technology": "💻",
                "bill_payment": "💡",
                "education": "🎓",
                "health": "🏥",
                "cash_withdrawal": "💵",
                "other": "🔧"
            }

            prompt = f"""
Aşağıdaki müşteri bilgisine ve harcama özetine göre, Türkçe olarak saygılı ve doğal bir dille bir özet yaz:
1. Müşteri adı: {customer_name}
2. Harcama kategorileri ve tutarlar (emoji destekli):
"""
            for category, amount in category_totals.items():
                emoji = category_emojis.get(category, "")
                prompt += f"- {emoji} {category.replace('_', ' ').title()}: {amount}\n"

            prompt += """
Metin şöyle başlamalı: "Sayın [Ad Soyad], hesap dökümünüzü inceledim. Analizlerime göre şu kategorilerde şu kadar harcama yapmışsınız:"
"""

            response = self.text_model.generate_content(prompt)
            print("🧠 Doğal dil özeti üretildi.")
            return response.text.strip()

        except Exception as e:
            print("❌ Özet oluşturulurken hata:", e)
            return "Özet oluşturulurken bir hata oluştu."
