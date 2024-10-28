from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.ext import ContextTypes, Application, CallbackQueryHandler
from mirror_bot.db.admindb import load_admin_list


async def handle_get_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admin_list = load_admin_list()
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_user.id, text=f"Error loading admin list: {e}")
        return

    if not admin_list:
        await context.bot.send_message(chat_id=update.effective_user.id, text="No admins found.")
        return

    buttons = [[InlineKeyboardButton(text=f"@{username}", callback_data=f"admin_actions:{username}")] for username in admin_list]
    await context.bot.send_message(chat_id=update.effective_user.id, text="Admins:", reply_markup=InlineKeyboardMarkup(buttons))



def register(application:Application):
    application.add_handler(CallbackQueryHandler(handle_get_admins, pattern=r"^get_admins"))