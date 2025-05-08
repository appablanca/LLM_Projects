import os, requests, sys, json
import google.generativeai as genai
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chat_models import init_chat_model
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pdf_text import main, get_first_txt_from_output_folder
api_key=os.getenv('GOOGLE_API_KEY') 


categorizerAgentRole = f"""
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

# class Agent:
#     def __init__(self, name, role):
#         self.name = name
#         self.role = role
#         generation_config = {
#             "temperature": 0.3,
#             "top_p": 0.95,
#             "top_k": 64,
#             "max_output_tokens": 8192,
#             "response_mime_type": "application/json"
#         }
#         self.model = genai.GenerativeModel(
#             model_name="gemini-2.0-flash",
#             generation_config=generation_config,
#             system_instruction=role,
#         )

#     def generate_response(self, prompt):
#         response = self.model.generate_content(prompt)
#         cleaned = response.text.strip().strip("`").strip()
#         if cleaned.startswith("json"):
#             cleaned = cleaned[4:].strip()
#         try:
#             return json.loads(cleaned)
#         except json.JSONDecodeError:
#             return response.text 
    
    



# class ExpenseAnalyzerAgent(Agent):
#     def categorize(self, raw_text: str) -> dict:
#         main()
#         raw_text = get_first_txt_from_output_folder()
#         response = self.generate_content("Şu metni dönüştür:\n"+raw_text)
#         cleaned = response.text.strip().strip("`").strip()
#         if cleaned.startswith("json"):
#             cleaned = cleaned[4:].strip()
#         try:
#             return json.loads(cleaned)
#         except json.JSONDecodeError as e:
#             print("❌ JSON parse hatası:", e)
#             print("🔁 Gelen yanıt:\n", response.text)
#             raise
        
        
        
        
# def route_request(user_input):
#     agent_key = orchestrator.generate_response(user_input).strip().lower()
#     print(f"Selected Agent: {agent_key}")
#     selected_agent = agents.get(agent_key)

#     if not selected_agent:
#         return "No suitable agent found for the request."
    
#     return selected_agent.generate_response(user_input)

# # Örnek kullanım:
# user_input = "Son harcamalarımı analiz edip kategori bazlı dağılım yapar mısın?"
# result = route_request(user_input)
# print(result)


# agents = {
#     "spending": Agent("SpendingAnalysisAgent", "You analyze spending and return categories."),
#     "invest": Agent("InvestmentAdvisor", "You give personalized investment advice."),
#     "survey": Agent("SurveyTaggerAgent", "You extract and tag survey responses."),
#     "expenseAnalyzerAgent": ExpenseAnalyzerAgent("ExpenseAnalyzerAgent", categorizerAgentRole),
#     "risk": Agent("RiskProfileAdvisor", "You determine risk tolerance by asking questions."),
# }   


# orchestrator = Agent("Orchestrator", 
#     """You are the main controller. A user will ask something.
#     Decide which agent should handle the request from this list:
#     - spending
#     - invest
#     - survey
#     - doc
#     - risk
#     Respond only with the agent key (e.g., "spending") in lowercase and no other words.
#     """
# )


# Langchain setup

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_output_tokens=8192,
    generation_config={
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json"
    },
)

# Tool: SpendingAnalysisAgent
def spending_analysis(user_input):
    return "📊 Spending analysis: Categorized data with top 3 categories and insights."

spending_tool = Tool(
    name="SpendingAnalysisAgent",
    func=spending_analysis,
    description="Analyze financial transactions and return categorized insights."
)
# Tool: ExpenseAnalyzerAgent
def categorize_expenses(raw_text):
    system_prompt = f"""
    Sen bir metin yapılandırma asistanısın. Aşağıda verilen ham metni incele ve bunu aşağıdaki JSON şemasına göre formatla.

    Kurallar:
    1. "türü", "musteri_bilgileri", "islemler", "kart_limiti", "kategori_toplamlari" ana alanlarını mutlaka oluştur.
    2. Tüm para değerlerini TL olarak bırak ve aynen aktar (virgül ve nokta biçimleri korunmalı).
    3. "islemler" kısmındaki her satırı dikkatli ayır: tarih, açıklama, tutar ve varsa maxipuan.
    4. "kategori_toplamlari" kısmında verilen kategorilere göre toplamları sınıflandır.
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
    Şu metni dönüştür:
    {raw_text}
    """

    # LangChain uyumlu LLM çağrısı
    response = llm.invoke(system_prompt)
    cleaned_text = response.content.strip().strip("`").strip()
    if cleaned_text.startswith("json"):
        cleaned_text = cleaned_text[4:].strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print("❌ JSON format hatası:", e)
        print("🧾 Yanıt içeriği:\n", response.content)
        raise

categorizer_tool = Tool(
    name="ExpenseAnalyzerAgent",
    func=categorize_expenses,
    description="Convert raw financial documents into structured JSON format."
)

# Tool: InvestmentAdvisor
def investment_advice(user_input):
    return "📈 Investment tips: Consider ASELS, TUPRS for Q2 portfolio."

investment_tool = Tool(
    name="InvestmentAdvisor",
    func=investment_advice,
    description="Give tailored investment recommendations."
)

# Tool: SurveyTaggerAgent
def tag_survey(user_input):
    return "📋 Survey categorized: Topics include income, housing, risk."

survey_tool = Tool(
    name="SurveyTaggerAgent",
    func=tag_survey,
    description="Analyze and tag user survey inputs."
)

# Tool: RiskProfileAdvisor
def risk_profile(user_input):
    return "⚠️ Risk profile: Medium. Recommend balanced investment."

risk_tool = Tool(
    name="RiskProfileAdvisor",
    func=risk_profile,
    description="Determine user’s financial risk tolerance."
)

# Combine tools
tools = [
    spending_tool,
    categorizer_tool,
    investment_tool,
    survey_tool,
    risk_tool
]

# Optional memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create new tool-calling agent
agent = create_tool_calling_agent(llm, tools)

# Wrap it in AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)




# Example interaction
if __name__ == "__main__":
    query = input("User: " )
    response = agent_executor.run(query)
    print(response)