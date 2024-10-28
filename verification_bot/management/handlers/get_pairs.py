from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, Application
from verification_bot.database import group_pairs_dao
from verification_bot.management.states import *

async def handle_get_pairs(update: Update, context: CallbackContext) -> None:
    """Displays the list of all group pairs with inline buttons."""
    pairs = group_pairs_dao.get_group_pairs()
    if not pairs:
        await update.message.reply_text("No group pairs found.")
        return ConversationHandler.END

    # Create inline buttons for each pair
    buttons = [create_group_pair_button(pair) for pair in pairs]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        text="Here is a list of all group pairs:",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END 


def create_group_pair_button(pair: dict) -> list:
        """Helper method to create a button for each group pair."""
        group1_title = pair.get("source_group_data", {}).get('title', 'Unknown Group 1')
        group2_title = pair.get("dest_group_data", {}).get('title', 'Unknown Group 2')
        button_text = f"{group1_title} <> {group2_title}"
        return [InlineKeyboardButton(text=button_text, callback_data='some_callback_data')]



def register(application: Application):
    """Registers handlers to the application."""
    application.add_handler(
        CommandHandler('getpairs', handle_get_pairs)
    )