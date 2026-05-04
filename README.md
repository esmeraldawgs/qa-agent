# 🚀 AI QA Test Scenario Generator

AI-powered QA assistant that generates and reviews test scenarios from PRD using a multi-agent approach (Generator + Reviewer).

---

## 🧠 Overview

This project simulates a real QA workflow enhanced by AI:

- **Generator Agent** → creates structured test scenarios from PRD  
- **Reviewer Agent** → validates, improves, and ensures coverage quality  

The system helps reduce manual effort while keeping test scenarios comprehensive and consistent.

---

## ⚙️ Tech Stack

- Python (Flask)
- Telegram Bot API
- DeepSeek (via OpenRouter)
- Cloud Hosting (Render)

---

## 🔁 Workflow

User (PRD) → Generator Agent → Reviewer Agent → Final Test Scenarios → Returned via Telegram

---

## 🤖 Features

- Generate test scenarios directly from PRD
- AI-based review & refinement (multi-agent flow)
- Covers:
  - Positive cases
  - Negative cases
  - Edge cases
  - Assumptions
- Simple Telegram interface
- Deployable on cloud (no local machine required)

---

## 📦 Installation (Local - Optional)

```bash
pip install -r requirements.txt
````

Create `.env` file:

```env
TELEGRAM_TOKEN=your_token_here
OPENROUTER_API_KEY=your_api_key_here
```

Run:

```bash
python main.py
```

---

## 🌐 Deployment

Deploy easily on Render:

1. Connect GitHub repository
2. Set build command:

   ```
   pip install -r requirements.txt
   ```
3. Set start command:

   ```
   python main.py
   ```
4. Add environment variables:

   * `TELEGRAM_TOKEN`
   * `OPENROUTER_API_KEY`

---

## 🧪 Usage

On Telegram:

```
/generate Login page must validate email and password
```

Bot will:

1. Generate test scenarios
2. Review and improve them
3. Return final output

---

## 💡 Why This Project?

Manual test case creation is:

* repetitive
* time-consuming
* prone to missing edge cases

This project demonstrates how AI can assist QA engineers by:

* speeding up test design
* improving coverage
* acting as a virtual QA reviewer

---

## 👩‍💻 Author

Esmeralda Wangsa
