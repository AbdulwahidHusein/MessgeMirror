from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
    ReplyKeyboardMarkup
)
from telegram.ext import ContextTypes,ConversationHandler, Application, CommandHandler, MessageHandler, filters
from models import TelegramWebhook
from mirror_bot.db.admindb import load_admin_list
from mirror_bot.db.database import (
    get_group_pairs, get_whitelist, get_sessions_by_user_id,
    update_session, delete_session, get_member_ship_groups
)
from mirror_bot.management.states import *
from mirror_bot.db.database import is_whitelisted, create_whitelist_entry
from utils.helpers import normalize_username


async def handle_add_to_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles adding a user to the whitelist."""
    await context.bot.send_message(chat_id=update.effective_user.id, text="Please forward a message from the user you wish to whitelist, or enter their username.")
    
    return WAITING_FOR_whitelist_USER


async def handle_whitelist_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the logic when waiting to whitelist a user."""
    message = update.message
    if message.forward_origin:
        await _process_forwarded_user(update, context)
    elif message.text:
        await process_whitelist_by_username(update, context)
    
    return ConversationHandler.END


async def _process_forwarded_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the forwarded user details for whitelisting."""
    message = update.message
    forward_origin = message.forward_origin
    sender_user = forward_origin.get("sender_user")

    if not sender_user:
        await context.bot.send_message(chat_id=update.effective_user.id, text="The forwarded user has a private profile, and their information cannot be accessed. Please send their username directly.")
        return

    user_id = sender_user["id"]
    first_name = sender_user.get("first_name", "Unknown")
    last_name = sender_user.get("last_name")
    username = message["from"].get("username")

    if is_whitelisted(user_id):
        await context.bot.send_message(chat_id=update.effective_user.id, text="This user is already in the whitelist. Please forward a message from a different user.")
        return

    success = create_whitelist_entry(user_id, first_name=first_name, last_name=last_name, username=username)
    if not success:
        await _send_generic_error_message(context)
        return False

    await context.bot.send_message(chat_id=update.effective_user.id, text="User has been successfully whitelisted.")
    return True



async def process_whitelist_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the whitelist operation when a username is provided."""
    message = update.message
    username = message.text

    if username.strip() == "":
        await context.bot.send_message(chat_id=update.effective_user.id, text="Invalid username.")
        return False

    normalized_username = normalize_username(username)[1:]
    
    if is_whitelisted(normalized_username):
        await context.bot.send_message(chat_id=update.effective_user.id, text="This user is already in the whitelist.")
        return False

    success = create_whitelist_entry(normalized_username)
    if not success:
        await _send_generic_error_message(context)
        await context.bot.send_message(chat_id=update.effective_user.id, text="An error occurred. Please try again later.")
        return False

    await context.bot.send_message(chat_id=update.effective_user.id, text="User has been successfully whitelisted.")
    return True

async def _send_generic_error_message(context: ContextTypes.DEFAULT_TYPE):
    """Send a generic error message."""
    await context.bot.send_message(chat_id=context.user_data["from_id"], text="Something went wrong. Please try again later.")



def register(application:Application):
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("addwhitelist", handle_add_to_whitelist)],
            states={
                WAITING_FOR_whitelist_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_whitelist_user)]
            },
            fallbacks=[],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )