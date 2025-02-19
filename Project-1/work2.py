import google.generativeai as genai
import os
from dotenv import load_dotenv

# API anahtarını yükle
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

chat_history = []

def chatbot_response(user_message):
    global chat_history 

    chat_history.append(f"User: {user_message}")

    conversation = "\n".join(chat_history)

    response = model.generate_content(conversation)

    chat_history.append(f"Bot: {response.text}")

    return response

while True:
    user_message = input("User: ")
    if user_message.lower() in ['exit', 'quit']:
        print("Exiting chat...")
        print("Chat history:", chat_history)
        break
    bot_response = chatbot_response(user_message)
    print("Bot:", bot_response.text)
    print("Tokens:", bot_response.usage_metadata)