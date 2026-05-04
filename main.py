import requests
from flask import Flask, request
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

app = Flask(__name__)

def call_ai(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

def generate(prd):
    return call_ai(f"""
You are a QA engineer.
Generate test scenarios from this PRD:
{prd}
""")

def review(tc):
    return call_ai(f"""
You are a strict QA reviewer.
Review and improve this:
{tc}
""")

def send_telegram(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if text.startswith("/generate"):
        prd = text.replace("/generate", "").strip()

        send_telegram(chat_id, "Generating...")

        tc = generate(prd)
        reviewed = review(tc)

        send_telegram(chat_id, reviewed)

    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

def call_ai(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        data = response.json()

        if "choices" not in data:
            return f"ERROR AI:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"EXCEPTION:\n{str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)