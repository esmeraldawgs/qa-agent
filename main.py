import os
import requests
from flask import Flask, request
from time import time
import threading

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

app = Flask(__name__)

# =========================
# DEDUP + RATE LIMIT
# =========================
processed_messages = set()
user_last_call = {}

def is_rate_limited(user_id):
    now = time()
    last = user_last_call.get(user_id, 0)
    if now - last < 10:
        return True
    user_last_call[user_id] = now
    return False


# =========================
# AI CALL (IMPROVED DEBUG)
# =========================
def call_ai(prompt, label="AI"):
    try:
        r = requests.post(
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

        data = r.json()
        print(f"[{label}] RAW RESPONSE:", data)

        if "choices" not in data:
            return f"AI ERROR ({label}): {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"[{label}] EXCEPTION:", str(e))
        return f"AI EXCEPTION ({label}): {str(e)}"


def generate(prd):
    return call_ai(f"""
You are a QA engineer.
Generate clean test scenarios from this PRD:

{prd}
""", "GENERATE")


def review(tc):
    return call_ai(f"""
You are a strict QA reviewer.
Improve and validate these test cases:

{tc}

Return ONLY final cleaned version.
""", "REVIEW")


# =========================
# TELEGRAM SEND
# =========================
def send_telegram(chat_id, text):
    try:
        text = str(text)

        if len(text) > 3500:
            text = text[:3500] + "\n\n...truncated"

        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=20
        )

        print("[TELEGRAM] RESPONSE:", r.text)

    except Exception as e:
        print("[TELEGRAM ERROR]:", str(e))


# =========================
# WEBHOOK
# =========================
@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("INCOMING:", data)

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")
    message_id = message.get("message_id")

    if not chat_id or not message_id:
        return "no data"

    unique_key = f"{chat_id}:{message_id}"

    if unique_key in processed_messages:
        return "ignored"

    processed_messages.add(unique_key)

    if not text.startswith("/generate"):
        return "ok"

    if is_rate_limited(user_id):
        send_telegram(chat_id, "Tunggu 10 detik ya bestie 😏")
        return "ok"

    prd = text.replace("/generate", "").strip()

    send_telegram(chat_id, "Generating QA scenarios...")

    # =========================
    # SAFE THREAD EXECUTION
    # =========================
    def worker():
        try:
            print("[WORKER] GENERATE START")
            tc = generate(prd)
            print("[WORKER] GENERATE DONE")

            print("[WORKER] REVIEW START")
            reviewed = review(tc)
            print("[WORKER] REVIEW DONE")

            send_telegram(chat_id, reviewed)
            print("[WORKER] SENT DONE")

        except Exception as e:
            print("[WORKER ERROR]:", str(e))
            send_telegram(chat_id, f"WORKER ERROR: {str(e)}")

    threading.Thread(target=worker, daemon=True).start()

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