from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, Application
from verification_bot.database import group_pairs_dao


async def handle_remove_pair(update: Update, context: CallbackContext) -> int:
    """Initiates the removal of a group pair by displaying all existing pairs."""
    # Fetch all existing group pairs
    pairs = group_pairs_dao.get_group_pairs()
    if not pairs:
        await update.message.reply_text("No group pairs found.")
        return
    buttons = [
        [
            InlineKeyboardButton(
                text=f"From {pair['source_group_data']['title']} <to> {pair['dest_group_data']['title']}",
                callback_data=f"remove_pair:{pair['source_group_data']['id']}"
            )
        ]
        for pair in pairs
    ]
    # Send message with inline keyboard for selecting the pair to remove
    await update.message.reply_text(
        text="Select a group pair to remove:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_remove_pair_inline(update: Update, context: CallbackContext) -> int:
    """Handles the inline callback for removing a selected group pair."""
    
    # Parse the callback data to get the group ID for the pair to remove
    callback_data = update.callback_query.data
    try:
        group_id = int(callback_data.split(":")[1])
    except (ValueError, IndexError):
        await update.callback_query.answer(text="Invalid group selection. Please try again.")

    # Attempt to remove the pair and provide feedback to the user
    removed = group_pairs_dao.delete_group_pair(group_id)
    
    if removed:
        await update.callback_query.edit_message_text(text="Group pair removed successfully.")
    else:
        await update.callback_query.answer(text="Failed to remove group pair. Please try again.")
    



def register(application: Application):
    """Registers the handlers to the application."""
    application.add_handler(CommandHandler("removepair", handle_remove_pair))
    application.add_handler(CallbackQueryHandler(handle_remove_pair_inline, pattern=r"^remove_pair"))
