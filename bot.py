"""
💊 MediBuddy — Your Personal Medicine Guide on Telegram
Now with Supabase DB Tracking 🚀
"""

import logging
import os
import sys
from dotenv import load_dotenv
import psycopg2

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from groq import Groq

print("PYTHON VERSION:", sys.version)

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── ENV VARIABLES ──────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_KEY       = os.environ["GROQ_API_KEY"]
DATABASE_URL   = os.environ.get("DATABASE_URL")

# ── DATABASE CONNECTION (Supabase) ─────────────────────────────────────────
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()
    print("✅ Database connected successfully")
except Exception as e:
    print("❌ Database connection failed:", e)

# ── GROQ SETUP ─────────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_KEY)
MODEL  = "llama-3.3-70b-versatile"

# ── SYSTEM PROMPT ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are MediBuddy 💊 — a safe, reliable, and easy-to-understand medicine information guide designed for Indian users.

STRICT SAFETY RULES:
- Do NOT diagnose diseases
- Do NOT prescribe medicines
- Do NOT suggest exact dosages
- Always include a safety disclaimer

Keep answers simple, friendly, and structured.
"""

# ── USER MEMORY ────────────────────────────────────────────────────────────
user_histories: dict[int, list[dict]] = {}
MAX_HISTORY = 10

def get_history(user_id: int):
    return user_histories.setdefault(user_id, [])

def add_to_history(user_id: int, role: str, content: str):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY:
        user_histories[user_id] = history[-MAX_HISTORY:]

# ── SAVE QUERY TO DATABASE ─────────────────────────────────────────────────
def save_query(user_id, username, query):
    try:
        print("📥 Saving to DB:", user_id, username, query)

        cursor.execute(
            "INSERT INTO users_queries (user_id, username, query) VALUES (%s, %s, %s)",
            (user_id, username, query)
        )
        conn.commit()

        print("✅ Saved successfully")

    except Exception as e:
        print("❌ DB ERROR:", e)

# ── GROQ RESPONSE ──────────────────────────────────────────────────────────
def ask_groq(user_id: int, message: str) -> str:
    try:
        add_to_history(user_id, "user", message)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + get_history(user_id)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        add_to_history(user_id, "assistant", reply)

        return reply

    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "⚠️ Error occurred. Please try again later."

# ── COMMANDS ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories.pop(update.effective_user.id, None)
    await update.message.reply_text(
        "Hello! I am MediBuddy 💊\n\n"
        "Ask me about any medicine!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use me to understand medicines 💊")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories.pop(update.effective_user.id, None)
    await update.message.reply_text("🧹 History cleared!")

# ── TEXT HANDLER ───────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "unknown"
    text = update.message.text.strip()

    if not text:
        return

    print("📩 MESSAGE:", text)

    # 🔥 SAVE TO DATABASE
    save_query(user_id, username, text)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    reply = ask_groq(user_id, text)
    await update.message.reply_text(reply)

# ── PHOTO HANDLER ──────────────────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Please type the medicine names from the image 😊"
    )

# ── MAIN ───────────────────────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("🚀 MediBuddy is live!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()