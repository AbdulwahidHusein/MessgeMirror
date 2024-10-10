from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from model import TelegramWebhook
from database import delete_group_pair, delete_blacklist_entry, get_sessions_by_user_id, get_member_shipgroup_by_id, update_session, has_group_pair, create_group_pair
from states import WAITING_FOR_SECOND_GROUP

async def handle_callback_query(bot: Bot, webhook_data: TelegramWebhook):
    callback_query = webhook_data.callback_query
    user_id = callback_query['from']['id']
    callback_data = callback_query['data']
    message = callback_query.get('message', {})

    print(f"Callback query received: {callback_query}")

    # A mapping between callback actions and handler functions
    callback_handlers = {
        "remove_pair": handle_remove_pair,
        "confirm_remove_pair": handle_confirm_remove_pair,
        "remove_from_blacklist": handle_remove_from_blacklist,  
        "add_pair_inline": handle_add_pair_inline
    }

    # Determine the action and pass control to the corresponding handler
    action = callback_data.split(":")[0]
    if action in callback_handlers:
        await callback_handlers[action](bot, user_id, callback_data)
    else:
        await bot.send_message(chat_id=user_id, text="Unknown action. Please try again.")


async def handle_remove_pair(bot: Bot, user_id: int, callback_data: str):
    """Handle user confirmation to remove a group pair."""
    pair_id = callback_data.split(":")[1]
    await bot.send_message(
        chat_id=user_id,
        text="Are you sure you want to remove this group pair?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Yes", callback_data=f"confirm_remove_pair:{pair_id}"),
             InlineKeyboardButton(text="No", callback_data="cancel")]
        ])
    )


async def handle_confirm_remove_pair(bot: Bot, user_id: int, callback_data: str):
    """Confirm and remove a group pair by its ID."""
    try:
        pair_id = int(callback_data.split(":")[1])
        success = delete_group_pair(pair_id)
        if success:
            await bot.send_message(chat_id=user_id, text=f"Group pair with ID {pair_id} has been successfully removed.")
        else:
            await bot.send_message(chat_id=user_id, text=f"Failed to remove the group pair with ID {pair_id}. It may not exist.")
    except (ValueError, IndexError):
        await bot.send_message(chat_id=user_id, text="Invalid group pair ID. Please try again.")


async def handle_remove_from_blacklist(bot: Bot, user_id: int, callback_data: str):
    """Remove a user from the blacklist."""
    try:
        client_id = int(callback_data.split(":")[1])
        success = delete_blacklist_entry(client_id)
        if success:
            await bot.send_message(chat_id=user_id, text="User has been successfully removed from the blacklist.")
        else:
            await bot.send_message(chat_id=user_id, text="Failed to remove user from the blacklist. The user may not be blacklisted.")
    except (ValueError, IndexError):
        await bot.send_message(chat_id=user_id, text="Invalid user ID. Please try again.")


async def handle_add_pair_inline(bot: Bot, user_id: int, callback_data: str):
    """Handle adding a group pair through an inline keyboard."""
    try:
        group_id = int(callback_data.split(":")[1])
    except (ValueError, IndexError):
        await bot.send_message(chat_id=user_id, text="Invalid group ID. Please select a valid group.")
        return

    # Check if the group is already paired
    if has_group_pair(group_id):
        await bot.send_message(chat_id=user_id, text="This group is already paired. Please select another group.")
        return

    session = get_sessions_by_user_id(user_id)

    # Retrieve group information
    group_info = get_member_shipgroup_by_id(group_id)
    if not group_info or 'group_data' not in group_info:
        await bot.send_message(chat_id=user_id, text="Failed to retrieve group information. Please try again.")
        return

    # Check if the session is waiting for the first or second group
    if session is not None and session.get("previous_data") is None:
        await bot.send_message(chat_id=user_id, text="Now send me the username of the second group or add me to the group and send any message to the group, or select from the list of available groups.")
        update_session(user_id, WAITING_FOR_SECOND_GROUP, group_info['group_data'])

    elif session is not None and session.get("previous_data") is not None:
        previous_data = session.get("previous_data")
        
        # Check if the group is the same as the first group
        if previous_data.get("id") == group_id:
            await bot.send_message(chat_id=user_id, text="A group cannot be paired with itself. Please select a different group.")
            return
        
        # Create group pair
        create_group_pair(previous_data, group_info['group_data'])
        await bot.send_message(chat_id=user_id, text=f"Group pair created: {previous_data['title']} <> {group_info['group_data']['title']} successfully.")
        update_session(user_id, None, None)

    else:
        await bot.send_message(chat_id=user_id, text="Something went wrong! Please try again.")
