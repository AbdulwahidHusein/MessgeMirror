from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.ext import ContextTypes,ConversationHandler, Application, CommandHandler, CallbackQueryHandler
from mirror_bot.db.database import (
    get_group_pairs 
)

from mirror_bot.management.states import *
from mirror_bot.db.database import  delete_group_pair


async def handle_remove_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles removing a pair of groups."""
    pairs = get_group_pairs()
    if not pairs:
        await context.bot.send_message(chat_id=update.effective_user.id, text="No group pairs found.")
        return

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{pair['group1_data']['title']} <> {pair['group2_data']['title']}",
                callback_data=f"remove_pair:{pair['group1_data']['id']}:{pair['group2_data']['id']}")
        ]
        for pair in pairs
    ]
    
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Select a group pair to remove:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return WAITING_FOR_GROUP_DELETE_SELECTION



async def handle_remove_pair_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the callback for removing a group pair."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback to avoid any Telegram client warnings
    print("update reached here")

    try:
        group1_id, group2_id = map(int, query.data.split(":")[1:])
    except (ValueError, IndexError):
        await query.message.reply_text("Invalid group pair. Please select a valid pair.")
        return

    # Store the selected group pair in context for confirmation
    context.user_data["group_pair_to_remove"] = {
        "group1_id": group1_id,
        "group2_id": group2_id
    }

    # Ask for confirmation using callback query
    await query.message.reply_text(
        text=f"Are you sure you want to remove the pairs",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="Yes", callback_data="confirm_remove_pair"),
                InlineKeyboardButton(text="No", callback_data="cancel")
            ]
        ])
    )
    return WAITING_FOR_GROUP_DELETE_CONFIRM


async def handle_confirmation_for_removal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the user's confirmation for removing a group pair."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback to avoid any Telegram client warnings

    if query.data == "confirm_remove_pair":
        # Get the group pair info from context.user_data
        group_pair = context.user_data.get("group_pair_to_remove")
        if not group_pair:
            await query.message.reply_text("No group pair found for removal. Please try again.")
            return

        group1_id = group_pair["group1_id"]
        group2_id = group_pair["group2_id"]

        # Proceed with removing the group pair
        if delete_group_pair(group1_id):
            await query.message.reply_text(f"Successfully removed the pair: {group1_id} <> {group2_id}.")

            context.user_data.clear()  
            return ConversationHandler.END
        else:
            await query.message.reply_text("Failed to remove the group pair. Please try again.")

        # Clear session data after removal
        context.user_data.clear()
        return ConversationHandler.END

    elif query.data == "cancel":
        await query.message.reply_text("Group pair removal cancelled.")
        context.user_data.clear()  # Clear session data on cancellation
        return ConversationHandler.END

    else:
        await query.message.reply_text("Invalid response. Please reply with 'Yes' or 'No'.")
        return WAITING_FOR_GROUP_DELETE_CONFIRM



def register(application:Application):
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("removepair", handle_remove_pair)],
            states={
                WAITING_FOR_GROUP_DELETE_SELECTION: [CallbackQueryHandler(handle_remove_pair_inline, pattern=r'^remove_pair')],
                WAITING_FOR_GROUP_DELETE_CONFIRM: [CallbackQueryHandler(handle_confirmation_for_removal, pattern=r'^confirm_remove_pair|cancel')]
            },
            fallbacks=[],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )