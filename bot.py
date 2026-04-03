"""
💊 MediBuddy — Your Personal Medicine Guide on Telegram
Powered by Groq AI (Free) | Built for Indian Users
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from groq import Groq

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── API Setup ─────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_KEY       = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_KEY)
MODEL  = "llama-3.3-70b-versatile"   # Best free model on Groq

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are MediBuddy 💊 — a safe, reliable, and easy-to-understand medicine information providing guide designed for Indian users.
Your purpose is to clearly explain medicines and prescriptions in simple, non-technical English so that anyone can understand.

STRICT SAFETY RULES:
- Do NOT diagnose diseases
- Do NOT prescribe medicines
- Do NOT suggest exact dosages for individuals
- Only provide general usage guidance
- If the query is serious or unclear, always advise consulting a doctor
- Always include a safety disclaimer at the end of every response

TONE AND STYLE:
- Simple, friendly, and reassuring
- No medical jargon
- Short and structured answers with bullet points
- Do not scare the user

WHEN USER PROVIDES A MEDICINE NAME, respond in this exact format:

💊 Medicine: <name>

1️⃣ What is it?
   - Simple 1-2 line explanation

2️⃣ What is it used for?
   - 2-4 uses as bullet points

3️⃣ When & how to take it?
   - Before or after food, general timing

4️⃣ Common side effects
   - 2-4 simple points

5️⃣ Who should be careful?
   - Who should be careful (pregnant women, kidney patients, allergies etc.)

🔒 Safety Note:
   This is general information only. Always consult your doctor or pharmacist before taking any medicine.

WHEN USER SENDS MULTIPLE MEDICINES OR A PRESCRIPTION:
- Explain each medicine briefly using the above format
- Then add: 🧾 Summary — why these medicines may be given together

WHEN USER ASKS SAFETY QUESTIONS (alcohol, food, mixing medicines):
- Start with: ✅ Yes / ❌ No / ⚠️ Depends
- Give 1-2 line explanation
- End with safety note

WHEN INPUT IS UNCLEAR:
- Ask a short, polite follow-up question

LANGUAGE RULE:
- Default: English
- If user writes in Hindi, reply in simple Hindi

GOAL: Make every user feel: I finally understood my medicine clearly, without confusion.
"""

# ── Per-user conversation history ─────────────────────────────────────────────
user_histories: dict[int, list[dict]] = {}
MAX_HISTORY = 10


def get_history(user_id: int) -> list[dict]:
    return user_histories.setdefault(user_id, [])


def add_to_history(user_id: int, role: str, content: str):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY:
        user_histories[user_id] = history[-MAX_HISTORY:]


# ── Ask Groq ──────────────────────────────────────────────────────────────────
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
        return (
            "⚠️ Sorry, I am having a little trouble right now. Please try again in a moment.\n\n"
            "If this is urgent, please consult a doctor or pharmacist directly. 🏥"
        )


# ── /start Command ────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories.pop(update.effective_user.id, None)
    await update.message.reply_text(
        "Hello! I am MediBuddy 💊\n\n"
        "Your personal medicine guide — simple, safe and in easy language!\n\n"
        "Here is what you can ask me:\n"
        "• 💊 Type any medicine name — I will explain it clearly\n"
        "• 📋 Send a list of medicines or a prescription\n"
        "• ⚠️ Ask safety questions — alcohol, food, combinations\n\n"
        "I understand English and Hindi\n\n"
        "🔒 I only provide general information. Always consult your doctor for medical advice."
    )


# ── /help Command ─────────────────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ How to use MediBuddy:\n\n"
        "1. Type a medicine name → get a full, clear explanation\n"
        "2. List multiple medicines → each one gets explained + summary\n"
        "3. Ask a safety question → get a quick ✅/❌/⚠️ answer\n\n"
        "Commands:\n"
        "/start — Restart the bot\n"
        "/clear — Clear your chat history\n"
        "/help — Show this help message\n\n"
        "🔒 Always consult a doctor or pharmacist for personal medical advice."
    )


# ── /clear Command ────────────────────────────────────────────────────────────
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories.pop(update.effective_user.id, None)
    await update.message.reply_text(
        "🧹 Chat history cleared! Starting fresh.\n\n"
        "Go ahead — ask me about any medicine 💊"
    )


# ── Text Message Handler ──────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id   = update.effective_user.id
    user_text = update.message.text.strip()

    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_groq(user_id, user_text)
    await update.message.reply_text(reply)


# ── Photo Handler (Groq doesn't support vision, guide user to type) ───────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 I can see you sent a photo!\n\n"
        "Please type out the medicine names written on the prescription and I will explain each one clearly. 😊"
    )


# ── Main Entry Point ──────────────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("🚀 MediBuddy is live and running!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()