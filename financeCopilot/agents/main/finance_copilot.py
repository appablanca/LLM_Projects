import os, requests, sys, json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.colab import userdata
import fitz
# api_key= userdata.get('GEMINI_API_KEY')
api_key=os.getenv('GEMINI_API_KEY')
expenseAnalyzerRole = f"""
Sen bir metin yapılandırma asistanısın. Aşağıda verilen ham metni incele ve bunu aşağıdaki JSON şemasına göre formatla.

Kurallar:
1. "türü", "musteri_bilgileri", "islemler", "kart_limiti", "kategori_toplamlari" ana alanlarını mutlaka oluştur.
2. Tüm para değerlerini TL olarak bırak ve aynen aktar (virgül ve nokta biçimleri korunmalı).
3. "islemler" kısmındaki her satırı dikkatli ayır: tarih, açıklama, tutar ve varsa maxipuan.
4. "kategori_toplamlari" kısmında verilen kategorilere göre toplamları sınıflandır. Kategori listesi aşağıda.
5. Bilgi eksikse null değeri kullan.
6. JSON biçimi geçerli ve düzenli olmalı.

Kategoriler:
["yeme_icme", "giyim_kozmetik", "abonelik", "market", "ulasim", "eglence", "kirtasiye_kitap", "teknoloji", "fatura_odeme", "egitim", "saglik", "nakit_cekme", "diger"]

JSON Formatı:
{{
  "türü": "fiş/fatura/hesap dökümü",
  "musteri_bilgileri": {{
    "ad_soyad": "MELİSA SUBAŞI"
  }},
  "islemler": [...],
  "kart_limiti": {{
    "toplam_kart_limiti": "2.000,00 TL"
  }},
  "kategori_toplamlari": {{
    "yeme_icme": "1.819,00 TL"
  }}
}}
"""

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction=role,
        )

    def generate_response(self, prompt):
        response = self.model.generate_content(prompt)
        cleaned = response.text.strip().strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return response.text

class ExpenseAnalyzerAgent(Agent):

    def extract_text_from_pdf(pdf_path):
            doc = fitz.open(pdf_path)
            all_text = ""
            for page in doc:
                all_text += page.get_text()
            return all_text

    def get_first_txt_from_output_folder(self):
        txt_files = [f for f in os.listdir(CIKTI_KLASORU) if f.endswith(".txt")]
        if not txt_files:
            raise FileNotFoundError("cikti_klasoru içinde .txt dosyası yok.")
        first_txt_path = os.path.join(CIKTI_KLASORU, txt_files[0])
        with open(first_txt_path, "r", encoding="utf-8") as f:
            return f.read()


    def main(self):
        if not os.path.exists(CIKTI_KLASORU):
            os.makedirs(CIKTI_KLASORU)

        for filename in os.listdir(GIRDI_KLASORU):
            filepath = os.path.join(GIRDI_KLASORU, filename)
            if os.path.isfile(filepath) and filepath.lower().endswith(".pdf"):
                print(f"İşleniyor (PDF): {filename}")
                text = self.extract_text_from_pdf(filepath)
                if text.strip():
                    output_filename = os.path.splitext(filename)[0] + ".txt"
                    output_path = os.path.join(CIKTI_KLASORU, output_filename)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"Kaydedildi: {output_filename}")
                else:
                    print(f"PDF boş veya metin çıkarılamadı: {filename}")
            else:
                print(f"Atlandı (PDF değil): {filename}")

    def categorize(self, raw_text: str) -> dict:
        self.main()
        raw_text = self.get_first_txt_from_output_folder()
        response = self.generate_response("Şu metni dönüştür:\n"+raw_text)
        cleaned = response.text.strip().strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print("❌ JSON parse hatası:", e)
            print("🔁 Gelen yanıt:\n", response.text)
            raise

class Orcestrator(Agent):

    def route_request(self, user_input):
        agent_key = self.generate_response(user_input).strip().lower()
        print(f"Selected Agent: {agent_key}")
        selected_agent = agents.get(agent_key)

        if not selected_agent:
            return "No suitable agent found for the request."

        return selected_agent.generate_response(user_input)

agents = {
    "spending": Agent("SpendingAnalysisAgent", "You analyze spending and return categories."),
    "invest": Agent("InvestmentAdvisor", "You give personalized investment advice."),
    "survey": Agent("SurveyTaggerAgent", "You extract and tag survey responses."),
    "expenseAnalyzerAgent": ExpenseAnalyzerAgent("ExpenseAnalyzerAgent", expenseAnalyzerRole),
}

orchestrator = Orcestrator("Orchestrator",
    """You are the main controller. A user will ask something.
Decide which agent should handle the request from this list:
- spending
- invest
- survey
- expenseanalyzeragent

Respond only with **one** of the above keys in **lowercase**, with **no explanations or extra text**.
Just the key, nothing else. For example: "spending"
"""
)

if __name__ == "__main__":
    while(True):
        user_input= input("User: ")
        if(user_input == "exit"):
            break

        result=orchestrator.route_request(user_input)
        print(result)