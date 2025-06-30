from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from google.cloud import bigquery
from dotenv import load_dotenv
from openai import OpenAI
import os
from src.bot.utils import (
    get_language_prompt,
    get_greeting_message,
    get_default_response,
    extract_category,
    format_response
)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Twilio client
twilio_client = Client(
    os.getenv("WHATSAPP_API_SID"),
    os.getenv("WHATSAPP_API_TOKEN")
)
whatsapp_number = os.getenv("WHATSAPP_PHONE_NUMBER")

# Initialize BigQuery client
bq_client = bigquery.Client.from_service_account_json(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)
dataset_id = os.getenv("BIGQUERY_DATASET")
table_id = os.getenv("BIGQUERY_TABLE")

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory session storage (phone number -> language)
user_sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages via Twilio webhook."""
    # Extract message and sender
    incoming_msg = request.values.get("Body", "").lower().strip()
    from_number = request.values.get("From", "")
    
    # Create TwiML response
    resp = MessagingResponse()
    
    # Check if user has selected a language
    if from_number not in user_sessions:
        if incoming_msg in ["english", "hinglish"]:
            user_sessions[from_number] = incoming_msg
            greeting = get_greeting_message(incoming_msg)
            resp.message(f"{greeting}\n👉 How can I help you today?")
        else:
            resp.message(get_language_prompt())
        return str(resp)
    
    # Get user's language preference
    language = user_sessions[from_number]
    
    # Handle reset command to restart session
    if incoming_msg == "reset":
        del user_sessions[from_number]
        resp.message(get_language_prompt())
        return str(resp)
    
    # Process query with ChatGPT-4o
    try:
        chatgpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are a friendly WhatsApp bot for Indian users, helping them find AI tools. "
                    "Respond in short, engaging sentences with emojis. "
                    "Use a conversational tone and subtly nudge users toward relevant AI tools. "
                    f"Reply in {language} (English or Hinglish). "
                    "Map the user's query to one of these categories: Website Creation & Design, "
                    "SEO & Content Optimization, Copywriting & Blogging, Video Creation & Editing, "
                    "Image Generation & Graphic Design, Email Marketing & Outreach, Social Media Management, "
                    "Text-to-Speech & Voice Cloning, Podcast & Audio Editing, Resume & Career Tools, "
                    "Chatbots & Virtual Assistants, E-commerce Support, Idea Generation & Planning, "
                    "Learning & Tutoring, Code Assistance, Cybersecurity & Privacy, Music & Audio Generation, "
                    "Research & Summarization, Translation & Subtitling, Ads & Creatives, LLM-based Agents, "
                    "Meeting Tools, Hosting."
                )},
                {"role": "user", "content": incoming_msg}
            ],
            max_tokens=100
        )
        category = extract_category(chatgpt_response.choices[0].message.content.lower())
        
        if not category:
            resp.message(get_default_response(language))
            return str(resp)
        
        # Query BigQuery for tools
        query = f"""
        SELECT tool_name, use_case, affiliate_link, affiliate_amount
        FROM `{os.getenv('GOOGLE_CLOUD_PROJECT_ID')}.{dataset_id}.{table_id}`
        WHERE category LIKE '%{category}%' AND affiliate_link IS NOT NULL
        ORDER BY affiliate_amount DESC
        LIMIT 3
        """
        query_job = bq_client.query(query)
        tools = list(query_job.result())
        
        if not tools:
            resp.message(get_default_response(language, category=category))
        else:
            response = format_response(tools, category, language)
            resp.message(response)
    except Exception as e:
        resp.message(get_default_response(language, error=str(e)))
    
    return str(resp)

if __name__ == "__main__":
    # Local testing: Simulate a message
    test_number = "whatsapp:+919876543210"  # Replace with your test number
    user_sessions[test_number] = "hinglish"  # Simulate Hinglish selection
    test_message = "Recommend SEO tools"
    
    try:
        chatgpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are a friendly WhatsApp bot for Indian users. "
                    "Map the query to a category like SEO & Content Optimization."
                )},
                {"role": "user", "content": test_message}
            ],
            max_tokens=100
        )
        category = extract_category(chatgpt_response.choices[0].message.content.lower())
        query = f"""
        SELECT tool_name, use_case, affiliate_link, affiliate_amount
        FROM `{os.getenv('GOOGLE_CLOUD_PROJECT_ID')}.{dataset_id}.{table_id}`
        WHERE category LIKE '%{category}%' AND affiliate_link IS NOT NULL
        ORDER BY affiliate_amount DESC
        LIMIT 3
        """
        query_job = bq_client.query(query)
        tools = list(query_job.result())
        response = format_response(tools, category, "hinglish")
        print(f"Test Response:\n{response}")
    except Exception as e:
        print(f"Test Error: {str(e)}")
    
    # Run Flask app for local development
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
