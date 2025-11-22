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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://telegram-7cvg.onrender.com

logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! Пиши мне 🙂")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        await update.message.chat.send_action("typing")
        resp = client.responses.create(model="gpt-4.1-mini", input=text)
        answer = resp.output_text
    except Exception as e:
        answer = "Ошибка OpenAI: " + str(e)

    await update.message.reply_text(answer)


async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # запускаем ТОЛЬКО webhook-сервер, без дополнительных циклов
    await app.initialize()
    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    await app.start()
    await app.updater.start_polling()  # НЕТ! polling не нужен

    # правильный метод PTB для webhook:
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
