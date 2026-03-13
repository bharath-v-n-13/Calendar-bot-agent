import os
import sys
import io
import logging

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv

# load environment variables before importing other modules
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import cmd_start, cmd_help, cmd_clear, handle_message

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

def main():
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("GEMINI_API_KEY"):
        logging.error("Missing TELEGRAM_BOT_TOKEN or GEMINI_API_KEY in .env file!")
        return

    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CommandHandler("clear", cmd_clear))
    
    # handle normal text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot with Google Calendar is running...")
    cwd = os.getcwd()
    if not os.path.exists(os.path.join(cwd, 'credentials.json')):
        print("⚠️ Warning: 'credentials.json' not found. Google Calendar tasks will return an error.")
        print("Please download Desktop Client OAuth credentials from Google Cloud Console.")
        
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
