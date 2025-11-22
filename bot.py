import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

# ENV
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://telegram-7cvg.onrender.com

# Logging
logging.basicConfig(level=logging.INFO)

# OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! Пиши мне 🙂")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        await update.message.chat.send_action("typing")
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=text
        )
        answer = resp.output_text
    except Exception as e:
        answer = f"Ошибка OpenAI: {e}"
    await update.message.reply_text(answer)


# --- MAIN ---

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Устанавливаем webhook
    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    # Запускаем webhook сервер PTB (БЕЗ Flask, БЕЗ asyncio.run)
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
