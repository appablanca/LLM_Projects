import google.generativeai as genai
import os
import time
import random
import string
import logging

from google.colab import userdata
genai.configure(api_key=userdata.get('GEMINI_API_KEY3'))

model = genai.GenerativeModel("gemini-1.5-flash")


logging.getLogger("tornado.access").setLevel(logging.ERROR)

CONTEXT_WINDOW_LIMIT = 1_000_000
TOKEN_WARNING_THRESHOLD = int(CONTEXT_WINDOW_LIMIT * 0.8)
MAX_RETRIES = 5
INITIAL_DELAY = 2

chat_history = []
total_tokens_used = 0

def tokenCount(text):
    try:
        return model.count_tokens(text).total_tokens
    except Exception as e:
        print(f"An error occurred while counting tokens: {e}")
        return 0

def generate_text(conversation):
    global total_tokens_used
    retries = 0
    delay = INITIAL_DELAY

    while retries < MAX_RETRIES:
        try:
            count = tokenCount(conversation)

            while count>= CONTEXT_WINDOW_LIMIT:
                print("\nContext window exceeded! Removing old messages to stay within the limit.\n")
                chat_history.pop(0)
                conversation = "\n".join(chat_history)
                count = tokenCount(conversation)


            bot_response = model.generate_content(conversation)

            if bot_response:
               total_tokens_used = getattr(bot_response.usage_metadata, "total_token_count", 0)

            if total_tokens_used >= TOKEN_WARNING_THRESHOLD:
                print("\nWarning: You have used over 800,000 tokens! Consider summarizing your messages.\n")

            return bot_response

        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f"Rate limit reached. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
                delay *= 2
            else:
                print(f"API Error: {e}")
                return None

    print("Max retries reached. Please try again later.")
    return None

def chatbot_mode(user_message):
    global chat_history
    chat_history.append(f"User: {user_message}")
    conversation = "\n".join(chat_history)
    bot_response = generate_text(conversation)

    if bot_response:
        chat_history.append(f"{bot_response.text}")
        total_tokens_used = getattr(bot_response.usage_metadata, "total_token_count", 0)

        return bot_response
    return None

def rateLimitTest():
    print("Starting rate limit test: Sending 1500 requests...")
    for i in range(1500):
        print(f"Request {i+1}/1500")
        print("User: This is a rate limit test.")
        response = chatbot_mode("This is a rate limit test.")
        if response:
            print(f"Bot: {response.text}\n")
        else:
            print("Request failed or rate limit reached.\n")
            break

def generate_random_text(length):
    return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))

def contextWindowTest():
    test_message = generate_random_text(450000)
    response = chatbot_mode(test_message)
    if response:
        print(f"Bot: {response.text}...\n")
        print(response.usage_metadata)
    else:
        print("Request failed or context limit reached.\n")

print("\nChatbot is running. Type 'exit' to quit or 'rateLimitTest'/'contextWindowTest' to run the tests.\n")

while True:
    user_message = input("User: ")

    if user_message.lower() in ['exit', 'quit']:
        print("Exiting chat...")
        break

    if user_message.lower() == "ratelimittest":
        rateLimitTest()
        continue

    if user_message.lower() == "contextwindowtest":
        contextWindowTest()
        continue

    bot_response = chatbot_mode(user_message)

    if bot_response:
        print(f"Bot: {bot_response.text}")
        if bot_response and hasattr(bot_response, "usage_metadata"):
                print(bot_response.usage_metadata)
        else:
                print("Warning: API response does not contain usage metadata.")
                total_tokens_used = 0
    else:
        print("Bot: Unable to generate a response. Try again later.")
