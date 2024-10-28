from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, Application
from verification_bot.management.states import *
from verification_bot.database import whitelist_dao
from utils.helpers import normalize_username

async def handle_add_to_whitelist(update: Update, context: CallbackContext) -> int:
    """Initiates the whitelist process by asking for a forwarded message or username."""
    await update.message.reply_text(
        "Please forward a message from the user you wish to whitelist, or enter their username."
    )
    return WAITING_FOR_WHITELIST

async def handle_whitelist_user(update: Update, context: CallbackContext) -> int:
    """Handles the response for whitelisting, depending on whether it's a forwarded message or username."""
    message = update.message

    # Check if the message is forwarded
    if message.forward_origin:
        await process_forwarded_user(update, context)
    elif message.text:
        await process_whitelist_by_username(update, context)
    else:
        await update.message.reply_text("Invalid input. Please try again by forwarding a message or entering a username.")
    
    # End the conversation after processing
    return ConversationHandler.END

async def process_forwarded_user(update: Update, context: CallbackContext) -> None:
    """Processes the forwarded user for whitelisting."""
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
        await update.message.reply_text("This user is already whitelisted.")
        return

    user_dict = {
        "id": sender_user.id,
        "first_name": sender_user.first_name,
        "last_name": sender_user.last_name,
        "username": sender_user.username
    }
    success = whitelist_dao.add_to_whitelist(user_dict)
    if success:
        await update.message.reply_text("User has been successfully whitelisted.")
    else:
        await update.message.reply_text("Failed to add user to whitelist. Please try again.")

async def process_whitelist_by_username(update: Update, context: CallbackContext, username=None) -> None:
    """Processes the username provided for whitelisting."""
    if not username:
        username = update.message.text.strip()
    
    if not username:
        await update.message.reply_text("Invalid username. Please enter a valid username.")
        return

    normalized_username = normalize_username(username)[1:]
    if whitelist_dao.is_whitelisted(normalized_username):
        await update.message.reply_text("This user is already in the whitelist.")
        return

    success = whitelist_dao.add_to_whitelist_by_username(normalized_username)
    if success:
        await update.message.reply_text("User has been successfully whitelisted.")
    else:
        await update.message.reply_text("An error occurred. Please try again later.")

async def cancel_conversation(update: Update, context: CallbackContext) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("Whitelist process has been cancelled.")
    return ConversationHandler.END

def register(application: Application):
    """Registers handlers to the application."""
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('addwhitelist', handle_add_to_whitelist)],
            states={
                WAITING_FOR_WHITELIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_whitelist_user)]
            },
            fallbacks=[CommandHandler('cancel', cancel_conversation)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )
