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
from flask import Flask, request

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-service.onrender.com/webhook

client = OpenAI(api_key=OPENAI_API_KEY)

# Build bot app
tg_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

logging.basicConfig(level=logging.INFO)


# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает через веб-хуки!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("typing")
    resp = client.responses.create(model="gpt-4.1-mini", input=update.message.text)
    answer = resp.output_text
    await update.message.reply_text(answer)


# Add handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# Flask server for webhook
server = Flask(__name__)


@server.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.json, tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return "ok", 200


if __name__ == "__main__":
    # Set webhook
    import asyncio

    async def set_webhook():
        await tg_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    asyncio.run(set_webhook())

    # Start Flask server
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
