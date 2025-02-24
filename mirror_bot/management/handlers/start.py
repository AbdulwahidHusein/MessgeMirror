from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.ext import ContextTypes, Application, CommandHandler
from mirror_bot.db.admindb import load_admin_list
from keyboards.fixed import create_fixed_keyboard


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the bot by displaying available options with buttons."""
    commands = [
            "/addpair", "/removepair","/GetPairs", "/addwhitelist", "/Getwhitelist", "/removewhitelist", "/help", "/settings","/exit"
    ]

    keyboards = create_fixed_keyboard(commands)

    await update.message.reply_text(f"Welcome {update.effective_user.mention_html()}!", reply_markup=keyboards)

def register(application : Application):
    application.add_handler(CommandHandler("start", handle_start))
    
