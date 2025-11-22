import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# --- ENV ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # например https://telegram-7cvg.onrender.com

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- OpenAI client ---
client = OpenAI(api_key=OPENAI_API_KEY)


# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот на Render, можешь писать мне вопросы 🙂")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        await update.message.chat.send_action("typing")
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=text,
        )
        answer = resp.output_text
    except Exception as e:
        logging.exception("OpenAI error")
        answer = "Что-то пошло не так с OpenAI. Попробуй ещё раз позже."
    await update.message.reply_text(answer)


# --- MAIN ---

async def main():
    # создаём приложение
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # на всякий случай явно ставим вебхук
    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    # запускаем встроенный веб-сервер (БЕЗ Flask)
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook",
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
