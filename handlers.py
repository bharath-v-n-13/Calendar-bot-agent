import logging
from telegram import Update
from telegram.ext import ContextTypes
from loop import run_agent
from memory import conversation_history

logger = logging.getLogger(__name__)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm your *Personal Productivity Assistant* updated with *Google Calendar API*\n\n"
        "📅 Calendar Tasks  |  📝 Notes  |  🕐 Date & Time\n\n"
        "_Try: 'Add dentist appointment on Friday at 5pm' or 'Show my upcoming calendar events'_",
        parse_mode="Markdown"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*What I can do:*\n\n"
        "📅 *Google Calendar Tasks*\n"
        "• `add task Dentist Appt at 4pm on Friday`\n"
        "• `show my upcoming tasks`\n"
        "• `delete Dentist Appt`\n"
        "• `when is Diwali?` or `show festivals`\n\n"
        "📝 *Notes*\n"
        "• `save note: <text>`\n"
        "• `show my notes`\n\n"
        "🕐 *Date & Time*\n"
        "• `what time is it?`\n\n"
        "💬 Just talk naturally and I will organize it via Google Calendar!",
        parse_mode="Markdown"
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversation_history.pop(update.effective_user.id, None)
    await update.message.reply_text("🧹 History cleared!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = run_agent(user_id, update.message.text.strip())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        reply = f"⚠️ Something went wrong: {str(e)[:100]}"
    await update.message.reply_text(reply, parse_mode="Markdown")
