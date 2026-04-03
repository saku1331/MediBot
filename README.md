# 💊 MedSimplify — Telegram Medicine Guide Bot

MedSimplify is a free, AI-powered Telegram bot that explains medicines in simple, plain English for Indian users.
Built with Python · python-telegram-bot

---

## 🤖 Bot Details

| Field        | Value                    |
|--------------|--------------------------|
| Bot Name     | MedSimplify                |
| Username     | @MedSimplifyBot            |
| Language     | English + Hindi          |

---

## ✅ What MedSimplify Can Do

| User Input                          | Bot Response                              |
|-------------------------------------|-------------------------------------------|
| Type a medicine name                | Full explanation in plain English         |
| Send multiple medicine names        | Each explained + combined summary         |
| Send a prescription photo           | Reads image, explains all medicines       |
| Ask safety question (alcohol, food) | ✅ / ❌ / ⚠️ + simple explanation         |
| Write in Hindi                      | Replies in simple Hindi                   |
| /start                              | Welcome message + fresh session           |
| /clear                              | Clears chat memory                        |
| /help                               | Shows usage guide                         |

---

### STEP 3 — Set Up Project on Your Computer

Make sure you have **Python 3.10 or higher** installed.

```bash
# 1. Create your project folder
mkdir MedSimplify
cd MedSimplify

# 2. Place bot.py, requirements.txt, and .env.example inside this folder

# 3. Create a virtual environment
python -m venv venv

# 4. Activate the virtual environment
#    On Windows:
venv\Scripts\activate
#    On Mac / Linux:
source venv/bin/activate

# 5. Install all required packages
pip install -r requirements.txt
```

---

### STEP 4 — Add Your Secret Keys

```bash
# Rename the example file
cp .env.example .env
```

Now open the `.env` file in any text editor and fill in:

```
TELEGRAM_BOT_TOKEN=7123456789:AAxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

Save the file.

---

### STEP 5 — Run the Bot

```bash
python bot.py
```

You should see in the terminal:
```
🚀 MedSimplify is live and running!
```

Open Telegram, search for `@MedSimplifyBot`, press **Start**, and test it!

---

## ☁️ FREE CLOUD HOSTING (Run 24/7 Without Your PC)

### Option A — Railway.app ⭐ Recommended

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial MedSimplify bot"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/MedSimplify.git
   git push -u origin main
   ```

2. Go to → https://railway.app and sign up (free)
3. Click **New Project** → **Deploy from GitHub Repo**
4. Select your `MedSimplify` repository
5. Go to **Variables** tab → add:
   - `TELEGRAM_BOT_TOKEN` → your token
   - `ANTHROPIC_API_KEY` → your API key
6. Railway will auto-deploy. Your bot runs 24/7 for free!

---

### Option B — Render.com (Also Free)

1. Go to → https://render.com and sign up
2. Click **New** → **Background Worker**
3. Connect your GitHub repository
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Add your environment variables in the **Environment** tab
6. Click **Create Background Worker** — done!

---

## 📁 Project File Structure

```
MedSimplify/
├── bot.py              ← All bot logic lives here
├── requirements.txt    ← Python dependencies
├── .env                ← Your secret keys (NEVER share or commit this!)
├── .env.example        ← Safe template for reference
└── README.md           ← This setup guide
```

---

## 🔒 Safety Design

- MedSimplify **never** diagnoses any disease
- MedSimplify **never** prescribes or recommends dosages
- Every single response includes a safety disclaimer
- Always directs users to consult a real doctor for personal advice

---
