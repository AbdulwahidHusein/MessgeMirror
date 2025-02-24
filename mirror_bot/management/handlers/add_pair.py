from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.ext import ContextTypes,ConversationHandler, Application, CommandHandler, CallbackQueryHandler
from mirror_bot.db.database import (
 get_member_ship_groups
)

from mirror_bot.management.states import *
from mirror_bot.db.database import has_group_pair, get_member_shipgroup_by_id, create_group_pair

async def handle_add_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handles adding a pair of groups."""
    membership_groups = get_member_ship_groups()
    buttons = [[InlineKeyboardButton(text=f"{group['group_data']['title']}", callback_data=f"add_pair_inline:{group['group_data']['id']}")] for group in membership_groups if 'group_data' in group]

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Please provide the username of the first group or select from the list below.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    return WAITING_FOR_FIRST_GROUP



async def handle_add_pair_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handles the inline callback for selecting a group to add as a pair."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback to avoid any Telegram client warnings

    try:
        group_id = int(query.data.split(":")[1])
    except (ValueError, IndexError):
        await query.message.reply_text("Invalid group ID. Please select a valid group.")
        return WAITING_FOR_FIRST_GROUP

    if has_group_pair(group_id):
        await query.message.reply_text("This group is already paired. Please select another group.")
        return WAITING_FOR_FIRST_GROUP

    # Retrieve session data from context.user_data
    session_data = context.user_data.get("group_pairing_data")

    group_info = get_member_shipgroup_by_id(group_id)

    if not group_info or 'group_data' not in group_info:
        await query.message.reply_text("Failed to retrieve group information. Please try again.")
        return WAITING_FOR_FIRST_GROUP

    # First group selection
    if not session_data:
        await query.message.reply_text(
            "Now send me the username of the second group or add me to the group and send any message to the group, or select from the list of available groups."
        )
        # Save first group information in context.user_data
        context.user_data["group_pairing_data"] = group_info['group_data']
        context.user_data["status"] = WAITING_FOR_SECOND_GROUP
        return WAITING_FOR_SECOND_GROUP

    # Second group selection
    elif session_data:
        if session_data.get("id") == group_id:
            await query.message.reply_text("A group cannot be paired with itself. Please select a different group.")
            return WAITING_FOR_FIRST_GROUP

        # Create the group pair and clear session data
        create_group_pair(session_data, group_info['group_data'])
        await query.message.reply_text(
            f"Group pair created: {session_data['title']} <> {group_info['group_data']['title']} successfully."
        )
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        context.user_data.clear()  # Clear all session data after successful pairing
        return ConversationHandler.END

    await query.message.reply_text("Something went wrong! Please try again.")
    return WAITING_FOR_FIRST_GROUP


def register(application: Application):
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("addpair", handle_add_pair)],
            states={
                WAITING_FOR_FIRST_GROUP: [CallbackQueryHandler(handle_add_pair_inline, pattern=r'^add_pair_inline')],
                WAITING_FOR_SECOND_GROUP: [CallbackQueryHandler(handle_add_pair_inline, pattern=r'^add_pair_inline')],  
            },
            fallbacks=[],
            allow_reentry=True,
            per_chat=True,
            per_user=True
            
            
        )
    
    )
