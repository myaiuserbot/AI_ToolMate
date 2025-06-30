from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from google.cloud import bigquery
from dotenv import load_dotenv
from openai import OpenAI
import os
from utils import (
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
    incoming_msg = request.values.get("Body", "").lower().strip()
    from_number = request.values.get("From", "")
    
    resp = MessagingResponse()
    
    # Handle language selection
    if from_number not in user_sessions:
        if incoming_msg in ["english", "hinglish"]:
            user_sessions[from_number] = incoming_msg
            greeting = get_greeting_message(incoming_msg)
            resp.message(f"{greeting}\n👉 Kya aapko koi AI tool chahiye? Jaise 'SEO tools' ya 'Website builders'!")
            return str(resp)
        else:
            resp.message(get_language_prompt())
            return str(resp)
    
    language = user_sessions[from_number]
    
    # Handle session reset
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
                    f"Friendly WhatsApp bot for Indian users. Reply in {language} (English or Hinglish in English script). "
                    "Short, engaging responses with emojis. Map query to a category: Website Creation & Design, SEO & Content Optimization, "
                    "Copywriting & Blogging, Video Creation & Editing, Image Generation & Graphic Design, Email Marketing & Outreach, "
                    "Social Media Management, Text-to-Speech & Voice Cloning, Podcast & Audio Editing, Resume & Career Tools, "
                    "Chatbots & Virtual Assistants, E-commerce Support, Idea Generation & Planning, Learning & Tutoring, "
                    "Code Assistance, Cybersecurity & Privacy, Music & Audio Generation, Research & Summarization, "
                    "Translation & Subtitling, Ads & Creatives, LLM-based Agents, Meeting Tools, Hosting."
                )},
                {"role": "user", "content": incoming_msg}
            ],
            max_tokens=50
        )
        category = extract_category(chatgpt_response.choices[0].message.content.lower())
        
        if not category:
            resp.message(get_default_response(language))
            return str(resp)
        
        # Query BigQuery
        query = f"""
        SELECT tool_name, use_case, affiliate_link, affiliate_amount
        FROM `{os.getenv('GOOGLE_CLOUD_PROJECT_ID')}.{dataset_id}.{table_id}`
        WHERE category LIKE '%{category}%' AND affiliate_link IS NOT NULL
        ORDER BY CAST(affiliate_amount AS FLOAT64) DESC
        LIMIT 3
        """
        query_job = bq_client.query(query)
        tools = list(query_job.result())
        
        response = format_response(tools, category, language)
        resp.message(response)
    except Exception as e:
        resp.message(get_default_response(language, error=str(e)))
    
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
