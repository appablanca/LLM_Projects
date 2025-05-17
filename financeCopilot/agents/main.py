import os, sys, json
import gradio as gr
import google.generativeai as genai
from agents.baseAgent import Agent
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole
from agents.orcestratorAgent import Orcestrator, orcestratorAgentRole, agents
from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
import asyncio

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv('GEMINI_API_KEY') 

orchestrator = Orcestrator("Orchestrator", orcestratorAgentRole) 

# if __name__ == "__main__":
#     while(True):
#         user_input= input("User: ")
#         if(user_input == "exit"):
#             break
        
#         result=orchestrator.route_request(user_input)
#         print(result)

async def handle_user_input(user_text, uploaded_pdf):
    try:
        agent_key = orchestrator.get_agent_key(user_text)
        print(f"📎 Uploaded file: {uploaded_pdf.name if uploaded_pdf else 'None'}")

        for key in agents.keys():
            if key.lower() in agent_key:
                print(f"Selected Agent: {key}")
                if key == "expenseAnalyzerAgent":
                    if uploaded_pdf:
                        return agents[key].categorize_pdf(uploaded_pdf)
                    else:
                        return "Lütfen analiz edilecek bir PDF yükleyin."
                elif key == "lifePlannerAgent":
                    return await agents[key].get_life_plan(user_text)
                else:
                    return agents[key].generate_response(user_text)

        print("⚠️ Unknown agent key:", agent_key)
        return agents["normalChatAgent"].generate_response(user_text)
    except Exception as e:
        print(f"Error in handle_user_input: {e}")
        return {"error": "An error occurred while processing your request"}

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


