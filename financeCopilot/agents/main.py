import os, sys, json
import gradio as gr
import google.generativeai as genai
from agents.baseAgent import Agent
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent
from agents.orcestratorAgent import Orcestrator

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv('GEMINI_API_KEY') 





orchestrator = Orcestrator("Orchestrator", 
    """You are the main controller. A user will ask something.
    Decide which agent should handle the request from this list:
    - spendingAna
    - invest
    - survey
    - expenseAnalyzerAgent
    - normalChatAgent
    Respond only with the agent key (e.g., "spending") in lowercase and no other words.
    """
)


# if __name__ == "__main__":
#     while(True):
#         user_input= input("User: ")
#         if(user_input == "exit"):
#             break
        
#         result=orchestrator.route_request(user_input)
#         print(result)


def handle_user_input(user_text, uploaded_pdf):

  return orchestrator.route_request(user_text,uploaded_pdf)

iface = gr.Interface(
    fn=handle_user_input,
    inputs=[
        gr.Textbox(lines=2, label="Kullanıcı Mesajı (Opsiyonel)"),
        gr.File(file_types=[".pdf"], label="PDF Yükle (Opsiyonel)")
    ],
    outputs="json",
    title="Finans Asistanı",
    description="PDF yükleyerek harcama analizi alabilir ya da metin yazarak farklı görevleri tetikleyebilirsiniz.",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()


