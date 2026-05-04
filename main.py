import requests
from flask import Flask, request
import os
from time import time

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

app = Flask(__name__)

# =========================
# ANTI SPAM / DEDUP STORAGE
# =========================
processed_updates = set()
user_last_call = {}

# =========================
# RATE LIMIT
# =========================
def is_rate_limited(user_id):
    now = time()
    if user_id in user_last_call:
        if now - user_last_call[user_id] < 10:
            return True
    user_last_call[user_id] = now
    return False


# =========================
# AI CALL
# =========================
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
            },
            timeout=60
        )

        data = response.json()

        if "choices" not in data:
            return f"ERROR AI:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"EXCEPTION AI:\n{str(e)}"


def generate(prd):
    return call_ai(f"""
You are a QA engineer.
Generate test scenarios from this PRD:
{prd}
""")


def review(tc):
    return call_ai(f"""
You are a strict QA reviewer.
Review and improve this test cases:
{tc}
""")


# =========================
# TELEGRAM SEND
# =========================
def send_telegram(chat_id, text):
    try:
        text = str(text)

        if len(text) > 3500:
            text = text[:3500] + "\n\n... (trimmed)"

        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=20
        )

        print("TELEGRAM RESPONSE:", r.text)

    except Exception as e:
        print("TELEGRAM ERROR:", str(e))


# =========================
# WEBHOOK
# =========================
@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("INCOMING:", data)

    update_id = data.get("update_id")
    if update_id in processed_updates:
        return "ignored"
    processed_updates.add(update_id)

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")

    print("CHAT_ID:", chat_id)
    print("TEXT:", text)

    if not chat_id:
        return "no chat id"

    if not text.startswith("/generate"):
        return "ok"

    if is_rate_limited(user_id):
        send_telegram(chat_id, "Tunggu dulu ya bestie 😏 (rate limited)")
        return "ok"

    prd = text.replace("/generate", "").strip()

    send_telegram(chat_id, "Generating...")

    # run heavy work async (avoid Telegram timeout/resend)
    import threading

    def worker():
        tc = generate(prd)
        print("TC:", tc)

        reviewed = review(tc)
        print("REVIEW:", reviewed)

        send_telegram(chat_id, reviewed)

    threading.Thread(target=worker).start()

    return "ok"


# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)