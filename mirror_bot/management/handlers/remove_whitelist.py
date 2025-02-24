from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.ext import ContextTypes,ConversationHandler, Application, CommandHandler, CallbackQueryHandler
from mirror_bot.db.database import get_whitelist

from mirror_bot.management.states import *
from mirror_bot.db.database import  delete_whitelist_entry

async def handle_remove_from_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handles removing a user from the whitelist."""
    whitelists = get_whitelist()
    if not whitelists:
        await context.bot.send_message(chat_id=update.effective_user.id, text="No users are currently whitelisted.")
        return ConversationHandler.END  # End the conversation if no whitelisted users are found

    buttons = [await _create_whitelist_button(user) for user in whitelists]
    await _send_message_with_inline_keyboard(update, context, "Select a user to remove from the whitelist:", buttons)

    return WAITING_FOR_REMOVE_whitelist_USER

async def handle_remove_from_whitelist_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the callback when a user selects a person to remove from the whitelist."""
    try:
        client_id = int(update.callback_query.data.split(":")[1])
    except (ValueError, IndexError):
        client_id = update.callback_query.data.split(":")[1]

    success = delete_whitelist_entry(client_id)
    if success:
        await context.bot.send_message(chat_id=update.effective_user.id, text="User has been successfully removed from the whitelist.")
        await context.bot.delete_message(chat_id=update.effective_user.id, message_id=update.callback_query.message.message_id)
    else:
        await context.bot.send_message(chat_id=update.effective_user.id, text="Failed to remove user from the whitelist. The user may not be whitelisted.")

    return ConversationHandler.END

async def _create_whitelist_button(user: dict) -> list:
    """Helper method to create a button for each whitelisted user."""
    button_text = ""
    if user.get("first_name") is not None:
        button_text += f"{user.get('first_name', '')} "
    if user.get("last_name") is not None:
        button_text += f"{user.get('last_name', '')} "
    if len(button_text.strip()) == 0:
        if user.get("username") is not None:
            button_text += f"@{user.get('username', '')}"
    if button_text.strip() == "":
        button_text = str(user['userid'])
    
    button_text = f"{button_text} (Click to remove from whitelist)".strip() or str(user['userid'])
    return [InlineKeyboardButton(text=button_text, callback_data=f"remove_from_whitelist:{user['userid']}")]

async def _send_message_with_inline_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: list) -> int:
    """Helper method to send a message with inline keyboard buttons."""
    reply_markup = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(chat_id=update.effective_user.id, text=text, reply_markup=reply_markup)
    
def register(application:Application):
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("removewhitelist", handle_remove_from_whitelist)],
            states={
                WAITING_FOR_REMOVE_whitelist_USER: [CallbackQueryHandler(handle_remove_from_whitelist_callback, pattern=r'^remove_from_whitelist')]
            },
            fallbacks=[],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )