from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, CallbackQueryHandler, filters, Application
from verification_bot.management.states import *
from verification_bot.database import whitelist_dao


async def handle_remove_from_whitelist_start(update: Update, context: CallbackContext) -> int:
    """Starts the process of removing a user from the whitelist."""
    whitelists = whitelist_dao.get_whitelisted_users()
    if not whitelists:
        await update.message.reply_text("No users are currently whitelisted.")
        return ConversationHandler.END

    # Create inline buttons for each whitelisted user
    buttons = [[_create_whitelist_button(user)] for user in whitelists]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        text="Select a user to remove from the whitelist:",
        reply_markup=reply_markup
    )
    
    return WAITING_FOR_REMOVE_WHITELIST

def _create_whitelist_button(user: dict) -> InlineKeyboardButton:
    """Helper method to create a button for each whitelisted user."""
    button_text = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    if not button_text and user.get("username"):
        button_text = f"@{user.get('username')}"
    if not button_text:
        button_text = str(user['user_id'])
        
    button_text += " (Click to remove from whitelist)"
    return InlineKeyboardButton(text=button_text, callback_data=f"remove_from_whitelist:{user['user_id']}")

async def handle_remove_from_whitelist_confirm(update: Update, context: CallbackContext) -> int:
    """Confirms and removes a user from the whitelist based on the callback data."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    try:
        user_id = int(query.data.split(":")[1])
        removed = whitelist_dao.remove_from_whitelist(user_id)
        
        if removed:
            await query.edit_message_text("User successfully removed from the whitelist!")
        else:
            await query.edit_message_text("Something went wrong. Please try again.")
    except (ValueError, IndexError):
        username = query.data.split(":")[1]
        print(username)
        removed = whitelist_dao.remove_from_whitelist(username)
        if removed:
            await query.edit_message_text("User successfully removed from the whitelist!")
        else:
            await query.edit_message_text("Something went wrong. Please try again.")

    return ConversationHandler.END

async def cancel_conversation(update: Update, context: CallbackContext) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("Operation has been cancelled.")
    return ConversationHandler.END

def register(application: Application):
    """Registers handlers to the application."""
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('removewhitelist', handle_remove_from_whitelist_start)],
            states={
                WAITING_FOR_REMOVE_WHITELIST: [CallbackQueryHandler(handle_remove_from_whitelist_confirm, pattern=r"^remove_from_whitelist")]
            },
            fallbacks=[CommandHandler('cancel', cancel_conversation)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )
