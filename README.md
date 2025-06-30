AIToolMate
WhatsApp bot for Indian users to recommend AI tools with affiliate links, supporting English and Hinglish (Hindi in English script). Built with Flask, Twilio, ChatGPT-4o, and Google Cloud BigQuery.
Deployment on Render

Push to GitHub:
git clone https://github.com/your-username/AIToolMate.git
cd AIToolMate
git add .
git commit -m "Deploy AIToolMate to Render"
git push origin main


Create Web Service (https://dashboard.render.com):

Name: aitoolmate
Environment: Python
Region: Oregon (or Singapore for India)
Branch: main
Root Directory: /
Build Command: pip install -r requirements.txt
Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
Plan: Free (or Starter)
Auto-Deploy: Yes


Set Environment Variables (Settings > Environment):

WHATSAPP_API_SID: Twilio Account SID (https://console.twilio.com)
WHATSAPP_API_TOKEN: Twilio Auth Token
WHATSAPP_PHONE_NUMBER: whatsapp:+919876543210
GOOGLE_CLOUD_PROJECT_ID: GCP project ID
BIGQUERY_DATASET: AI_ToolMate_Tools
BIGQUERY_TABLE: All_AI_Tool_Data
GOOGLE_APPLICATION_CREDENTIALS: Paste service account JSON content
OPENAI_API_KEY: OpenAI API key (https://platform.openai.com)
PYTHON_VERSION: 3.9.0


Configure Twilio Webhook:

Get Render URL (e.g., https://aitoolmate.onrender.com).
In Twilio Console (https://console.twilio.com):
Go to Phone Numbers > Active numbers > Your WhatsApp number.
Set "When a message comes in":
Webhook URL: https://aitoolmate.onrender.com/webhook
HTTP Method: POST






Test:

Send "Hinglish" to WhatsApp number → Expect greeting and prompt.
Send "SEO tools" → Expect tool recommendations with affiliate links.
Send "reset" → Restart language selection.



Files

app.py: Flask app with Twilio webhook and ChatGPT-4o.
utils.py: Hinglish/English templates.
queries.sql: Optional BigQuery queries.
.env.example: Environment variable template.
requirements.txt: Dependencies.
render.yaml: Render deployment config.
.gitignore: Ignores sensitive files.

Notes

Hinglish uses English script (e.g., "Namaste! AIToolMate mein swagat hai!").
ChatGPT-4o prompt uses ~100 tokens/request.
Affiliate links from BigQuery (e.g., SEMrush, Hostinger).
