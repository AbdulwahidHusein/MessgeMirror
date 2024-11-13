from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler, Application, ContextTypes
from verification_bot.database import admin_dao


async def handle_settings_start(update: Update, context: CallbackContext) -> int:
    """Handles the settings command by displaying available options."""
    buttons = [
        [InlineKeyboardButton(text="View Admins", callback_data="get_admins:null")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Settings:", reply_markup=reply_markup)
    

async def handle_get_admins(update: Update, context: CallbackContext) -> int:
    """Handles displaying the list of admins."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    try:
        admin_list = admin_dao.load_admin_list()
    except Exception as e:
        await query.edit_message_text(text=f"Error loading admin list: {e}")
        return ConversationHandler.END

    if not admin_list:
        await query.edit_message_text(text="No admins found.")
        return ConversationHandler.END

    # Create buttons for each admin
    buttons = [[InlineKeyboardButton(text=f"@{username}", callback_data=f"admin_actions:{username}")] for username in admin_list]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(text="Admins:", reply_markup=reply_markup)

async def handle_exit(update: Update, context:ContextTypes.DEFAULT_TYPE ):
    """Handles the exit command by clearing the user's session."""
    context.user_data.clear()
    await update.message.reply_text("Session cleared")

def register(application: Application):
    """Registers handlers to the application."""
    application.add_handler(CommandHandler("settings", handle_settings_start))
    application.add_handler(CallbackQueryHandler(handle_get_admins, pattern=r"^get_admins"))
    application.add_handler(CommandHandler("exit", handle_exit))
