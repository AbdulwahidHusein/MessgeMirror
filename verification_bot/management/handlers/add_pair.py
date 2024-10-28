from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from verification_bot.management.states import *

from verification_bot.database import membership_dao, group_pairs_dao


async def handle_add_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    membership_groups = membership_dao.get_member_ship_groups()
    buttons = [[InlineKeyboardButton(text=f"{group['group_data']['title']}", callback_data=f"add_pair_inline:{group['group_data']['id']}")] for group in membership_groups if 'group_data' in group]
    await update.message.reply_text(
        "Select a source group to add:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return WAITING_FOR_SOURCE_GROUP



async def handle_add_pair_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles inline group pairing by accepting a group ID and checking if the group is valid."""

    # Retrieve user ID and callback data
    user_id = update.effective_user.id
    callback_data = update.callback_query.data

    # Parse group ID from the callback data
    try:
        group_id = int(callback_data.split(":")[1])
    except (ValueError, IndexError):
        await update.callback_query.answer(text="Invalid group ID. Please select a valid group.")
        if "prev_group_data" not in context.user_data:
            return WAITING_FOR_DEST_GROUP
        return WAITING_FOR_SOURCE_GROUP

    # Check if the group is already paired
    if group_pairs_dao.has_group_pair(group_id):
        await update.callback_query.answer(text="This group is already paired. Please select another group.")
        if "prev_group_data" not in context.user_data:
            return WAITING_FOR_DEST_GROUP
        return WAITING_FOR_SOURCE_GROUP

    # Fetch group information
    group_info = membership_dao.get_member_shipgroup_by_id(group_id)
    if not group_info or 'group_data' not in group_info:
        await update.callback_query.answer(text="Failed to retrieve group information. Please try again.")
        return ConversationHandler.END

    # Store initial group information in context.user_data if not previously set
    if "prev_group_data" not in context.user_data:
        context.user_data["prev_group_data"] = group_info['group_data']
        await context.bot.send_message(
            chat_id=user_id,
            text="Now send the username of the second group or add me to the group and send any message in the group, "
                 "or select from the list of available groups."
        )
        return WAITING_FOR_DEST_GROUP

    # Check if selected group is the same as the previously stored one
    prev_group_data = context.user_data["prev_group_data"]
    if prev_group_data.get("id") == group_id:
        await update.callback_query.answer(text="A group cannot be paired with itself. Please select a different group.")
        return WAITING_FOR_DEST_GROUP

    # Create the group pair
    success = group_pairs_dao.create_group_pair(prev_group_data, group_info['group_data'])
    if success:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Group pair created successfully: {prev_group_data['title']} <> {group_info['group_data']['title']}."
        )
        await update.callback_query.message.delete()
    else:
        await context.bot.send_message(chat_id=user_id, text="Failed to create group pair. Please try again.")
    
    # Clear user data and end the conversation
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation and clears the user data."""
    await context.user_data.clear()
    return ConversationHandler.END


def register(application:Application):
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('addpair', handle_add_pair)],
            states={
                WAITING_FOR_SOURCE_GROUP: [CallbackQueryHandler(handle_add_pair_inline, pattern='add_pair_inline')],
                WAITING_FOR_DEST_GROUP:  [CallbackQueryHandler(handle_add_pair_inline, pattern='add_pair_inline')],
                # WAITING_FOR_DEST_GROUP: [MessageHandler(filters.TEXT  & ~filters.COMMAND, handle_add_pair_inline)]
            },
            fallbacks=[CommandHandler('cancel', cancel_conversation)],
            allow_reentry=True,
            per_chat=True,
            per_user=True
        )
    )