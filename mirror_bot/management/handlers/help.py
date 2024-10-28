from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.ext import ContextTypes, Application, CallbackQueryHandler, ConversationHandler, CommandHandler
from mirror_bot.db.admindb import load_admin_list




async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sends a help message with a list of available commands."""
        help_message = """
    *🛠️ Available Commands:*

    1. *🔄 /start:* Start the bot and display available options.
    2. *➕ Add Group Pair:* Add a pair of groups. You can select from a list of groups the bot is a member of or provide a group username.
    3. *❌ Remove Group Pair:* Remove an existing group pair. You will be prompted to select among existing pairs to delete.
    4. *🚫 Add to whitelist:* Add a user to the whitelist so that their messages will not be mirrored.
    5. *✅ Remove from whitelist:* Remove a user from the whitelist so that their messages will be mirrored again.
    6. *📜 List Group Pairs:* List all group pairs.
    7. *⛔️ Show whitelist:* List all whitelisted users.
    8. *🚪 Exit:* End the current session and close the bot.

    """
        
        await context.bot.send_message(chat_id=update.effective_user.id, text=help_message, parse_mode='Markdown')
        
    
async def handle_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ends the current session and sends a session exit message."""
    await context.bot.send_message(chat_id=update.effective_user.id, text="Your session has been successfully closed.")
    context.user_data.clear()
    ConversationHandler.END


def register(application:Application):
      application.add_handler(CommandHandler("help", handle_help))
      application.add_handler(CommandHandler('exit', handle_exit))
