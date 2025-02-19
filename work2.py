import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def estimate_tokens(text):
    return len(text)  

def chatbot_response(message):
    response = model.generate_content(message)

    input_tokens = estimate_tokens(message)
    output_tokens = estimate_tokens(response.text)

    # print(f"Input Tokens: {input_tokens}")
    # print(f"Output Tokens: {output_tokens}")

    return response

while True:
    user_message = input("User: ")
    if user_message.lower() in ['exit', 'quit']:
        print("Exiting chat...")
        break
    bot_response = chatbot_response(user_message)
    print("Bot:", bot_response.text)
    print("Tokens:", bot_response.usage_metadata)