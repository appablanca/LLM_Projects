import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")

# Context window settings
CONTEXT_WINDOW_LIMIT = 1_000_000  # 1 million tokens
TOKEN_WARNING_THRESHOLD = int(CONTEXT_WINDOW_LIMIT * 0.8)  # 80% threshold

chat_history = []
total_tokens_used = 0  # Track token usage


def chatbot_response(user_message):
    global chat_history, total_tokens_used

    # Append user message
    chat_history.append(f"User: {user_message}")
    conversation = "\n".join(chat_history)

    # Get response from Gemini
    response = model.generate_content(conversation)

    # Debug: Print response to check the structure
    if not hasattr(response, "usage_metadata"):
        print("⚠️ Warning: API response does not contain usage metadata.")
        token_count = 0
    else:
        # Check if 'usage_metadata' has 'total_token_count'
        token_count = getattr(response.usage_metadata, "total_token_count", 0)

    total_tokens_used = token_count

    # Warn if approaching the context limit
    if total_tokens_used >= TOKEN_WARNING_THRESHOLD:
        print("\n⚠️ Warning: You have used over 800,000 tokens! Consider summarizing or restarting the conversation to prevent overflow.\n")

    # Handle context window overflow (truncate older messages)
    while total_tokens_used >= CONTEXT_WINDOW_LIMIT:
        print("\n🚨 Context window exceeded! Truncating older messages to stay within limit.\n")
        chat_history.pop(0)  # Remove oldest message
        conversation = "\n".join(chat_history)
        response = model.generate_content(conversation)
        total_tokens_used = getattr(response.usage_metadata, "total_token_count", 0)

    # Append bot response
    chat_history.append(f"Bot: {response.text}")

    return response


# Run chatbot loop
while True:
    user_message = input("User: ")
    if user_message.lower() in ['exit', 'quit']:
        print("Exiting chat...")
        print("Chat history:", chat_history)
        break

    bot_response = chatbot_response(user_message)
    print("Bot:", bot_response.text)
    print("Tokens used:", total_tokens_used)