import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI
from flask import Flask, request
import asyncio

# ENV variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Logging
logging.basicConfig(level=logging.INFO)

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create Telegram bot application
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Flask server
server = Flask(__name__)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен на webhook и работает 24/7!")


# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("typing")
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=update.message.text
    )
    answer = resp.output_text
    await update.message.reply_text(answer)


# Add handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# Webhook endpoint
@server.route("/webhook", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.json, tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return "ok", 200


async def main():
    # Set webhook
    await tg_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    # Start application (dispatcher)
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # Start Flask (webhook server)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
