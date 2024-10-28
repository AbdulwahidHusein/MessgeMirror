from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes,ConversationHandler, Application,CommandHandler

from mirror_bot.db.database import  get_whitelist

from mirror_bot.management.states import *


async def handle_get_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the list of all whitelisted users."""
    whitelisted_users = get_whitelist()
    
    if not whitelisted_users:
        await update.message.reply_text("No users have been whitelisted yet.")
        return ConversationHandler.END  # End the conversation if no users are whitelisted
    
    buttons = [_create_whitelist_button(user) for user in whitelisted_users]
    await _send_message_with_inline_keyboard(
        context=context,
        chat_id=update.effective_user.id,
        text="Here is a list of all whitelisted users:",
        buttons=buttons,
    )
    

def _create_whitelist_button(user: dict) -> list:
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


async def _send_message_with_inline_keyboard(context, chat_id: int, text: str, buttons: list):
    """Helper method to send a message with inline keyboard buttons."""
    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    

def register(application:Application):
    application.add_handler(CommandHandler("Getwhitelist", handle_get_whitelist))
    