import os, requests, sys, json
import google.generativeai as genai

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pdf_text import main, get_first_txt_from_output_folder
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
    def categorize(self, raw_text: str) -> dict:
        main()
        raw_text = get_first_txt_from_output_folder()
        response = self.generate_content("Şu metni dönüştür:\n"+raw_text)
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
    - spendingAna
    - invest
    - survey
    - expenseAnalyzerAgent
    Respond only with the agent key (e.g., "spending") in lowercase and no other words.
    """
)


if __name__ == "__main__":
    while(True):
        user_input= input("User: ")
        if(user_input == "exit"):
            break
        
        result=orchestrator.route_request(user_input)
        print(result)



