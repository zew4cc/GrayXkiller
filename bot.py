import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot.")

def main():
    async def handler(event, context):
        try:
            # Get bot token from environment variable
            TOKEN = os.getenv("7646067586:AAEDKJ5L0XIH2AE_747brjticllnfh9sQH8")
            if not TOKEN:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "BOT_TOKEN not set"})
                }

            # Initialize bot
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))

            # Process Telegram update
            body = json.loads(event.get("body", "{}"))
            update = Update.de_json(body, app.bot)
            await app.process_update(update)

            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    return handler

handler = main()