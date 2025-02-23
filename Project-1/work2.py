import google.generativeai as genai
import os
import time
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

# Retry settings
MAX_RETRIES = 3
INITIAL_DELAY = 2  # Start with 2 seconds

chat_history = []  # Stores chat conversation
total_tokens_used = 0  # Track token usage


def generate_text(user_message):
   
    global total_tokens_used

    retries = 0
    delay = INITIAL_DELAY

    while retries < MAX_RETRIES:
        try:
            response = model.generate_content(user_message)
            
            print("Chat History:", chat_history)
            print(response.usage_metadata)


            # Get token usage
            if not hasattr(response, "usage_metadata"):
                print("Warning: API response does not contain usage metadata.")
                token_count = 0
            else:
                token_count = getattr(response.usage_metadata, "total_token_count", 0)
                

            total_tokens_used = token_count
            # Warn if context window is close to the limit
            if total_tokens_used >= TOKEN_WARNING_THRESHOLD:
                print("\n Warning: You have used over 800,000 tokens! Consider summarizing your messages.\n")

            return response

        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f" Rate limit reached. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
                delay *= 2  # Exponential backoff
            else:
                print(f" API Error: {e}")
                return None

    print(" Max retries reached. Please try again later.")
    return None



def chatbot_mode(user_message):
    
    global chat_history, total_tokens_used

    # Append user message to chat history
    chat_history.append(f"User: {user_message}")
    conversation = "\n".join(chat_history)
    
    retries = 0
    delay = INITIAL_DELAY

    while retries < MAX_RETRIES:
        try:
            # Generate response using text generation function
            bot_response = generate_text(conversation)

            if bot_response:
                chat_history.append(f" {bot_response.text}")

                # Check if total tokens exceed the limit
                if total_tokens_used >= TOKEN_WARNING_THRESHOLD:
                    print("\n Warning: Conversation is reaching the token limit. Consider summarizing.\n")

                # Handle context overflow (truncate older messages)
                while total_tokens_used >= CONTEXT_WINDOW_LIMIT:
                    print("\n Context window exceeded! Removing old messages to stay within the limit.\n")
                    chat_history.pop(0)  # Remove oldest message
                    conversation = "\n".join(chat_history)
                    bot_response = generate_text(conversation)
                    total_tokens_used = getattr(bot_response.usage_metadata, "total_token_count", 0)

                return bot_response.text

            return None

        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f" Rate limit reached. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
                delay *= 2  # Exponential backoff
            else:
                print(f" API Error: {e}")
                return None

    print(" Max retries reached. Please try again later.")
    return None


print("\n Chatbot is running. Type 'exit' to quit.\n")

while True:
    user_message = input("User: ")

    if user_message.lower() in ['exit', 'quit']:
        print("Exiting chat...")
        break

    bot_response = chatbot_mode(user_message)

    if bot_response:
        print(f"Bot: {bot_response}")
        print(f"Total tokens used: {total_tokens_used}")
    else:
        print("Bot: Unable to generate a response. Try again later.")
