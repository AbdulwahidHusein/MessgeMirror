from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, Application
from verification_bot.management.states import *
from verification_bot.database import whitelist_dao
from utils.helpers import normalize_username


async def check_whitelist(update: Update, context: CallbackContext) -> int:
    """Initiates the process for checking if a user is whitelisted."""
    await update.message.reply_text(
        "Please forward a message from the user you wish to check, or enter their username."
    )
    return WAITING_FOR_WHITELIST_CHECK

async def handle_whitelist_check(update: Update, context: CallbackContext) -> int:
    """Processes forwarded user or username to check whitelist status."""
    message = update.message

    # Check if the message is forwarded
    if message.forward_origin:
        await process_forwarded_for_whitelist(update, context)
    elif message.text:
        await process_whitelist_by_username(update, context)
    else:
        await update.message.reply_text("Invalid input. Please try again by forwarding a message or entering a username.")
    
    # End the conversation after processing
    return ConversationHandler.END

async def process_forwarded_for_whitelist(update: Update, context: CallbackContext) -> None:
    """Processes the forwarded message to check whitelist status."""
    if not hasattr(update.message.forward_origin, "sender_user"):
        if hasattr(update.message.forward_origin, "sender_user_name"):
            await process_whitelist_by_username(update, context, username=update.message.forward_origin.sender_user_name)
            return
        await update.message.reply_text(
            "The forwarded user has a private profile, and their information cannot be accessed. Please send their username directly."
        )
        return
    sender_user = update.message.forward_origin.sender_user

    user_id = sender_user.id
    if whitelist_dao.is_whitelisted(user_id):
        await update.message.reply_text("This user is whitelisted.")
    else:
        await update.message.reply_text("This user is not whitelisted.")

async def process_whitelist_by_username(update: Update, context: CallbackContext, username=None) -> None:
    """Processes the username to check whitelist status."""
    if not username:
        username = update.message.text.strip()

    if not username:
        await update.message.reply_text("Invalid username. Please enter a valid username.")
        return

    normalized_username = normalize_username(username)[1:]
    if whitelist_dao.is_whitelisted(normalized_username):
        await update.message.reply_text("This user is whitelisted.")
    else:
        await update.message.reply_text("This user is not whitelisted.")

async def cancel_conversation(update: Update, context: CallbackContext) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("Operation has been cancelled.")
    return ConversationHandler.END

def register(application: Application):
    """Registers handlers to the application."""

    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('checkwhitelist', check_whitelist)],
            states={
                WAITING_FOR_WHITELIST_CHECK: [MessageHandler(filters.ALL, handle_whitelist_check)]
            },
            fallbacks=[CommandHandler('cancel', cancel_conversation)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )
