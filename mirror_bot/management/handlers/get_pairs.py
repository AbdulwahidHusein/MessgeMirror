from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler


from telegram.ext import ContextTypes,ConversationHandler

from mirror_bot.db.database import (
    get_group_pairs
)

async def handle_get_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the list of all group pairs."""
    pairs = get_group_pairs()
    
    if not pairs:
        await update.message.reply_text("No group pairs found.")
        return ConversationHandler.END  # End the conversation if no pairs are found
    
    # Create buttons with callback data for each group pair
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{pair['group1_data']['title']} <> {pair['group2_data']['title']}",
                callback_data=f"pair_{pair['group1_data']['id']}"  # Unique callback data for each pair
            )
        ]
        for pair in pairs
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message( 
        chat_id=update.effective_user.id,
        text="Here are the list of pairs",
        reply_markup=reply_markup
    )
       
    
def register(application:Application):
    application.add_handler(CommandHandler("GetPairs", handle_get_pairs))
    