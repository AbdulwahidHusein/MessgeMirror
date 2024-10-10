from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from model import TelegramWebhook
from mongo import delete_group_pair, delete_blacklist_entry, get_sessions_by_user_id, get_member_shipgroup_by_id, update_session, has_group_pair, create_group_pair
from states import *

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
    pair_id = callback_data.split(":")[1]
    await bot.send_message(
        chat_id=user_id,
        text="Are you sure?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Yes", callback_data=f"confirm_remove_pair:{pair_id}"),
             InlineKeyboardButton(text="No", callback_data="cancel")]
        ])
    )


async def handle_confirm_remove_pair(bot: Bot, user_id: int, callback_data: str):
    pair_id = callback_data.split(":")[1]
    success = delete_group_pair(int(pair_id))
    if success:
        await bot.send_message(chat_id=user_id, text=f"Successfully removed the pair: {pair_id}.")
    else:
        await bot.send_message(chat_id=user_id, text=f"Failed to remove the pair: {pair_id}.")


async def handle_remove_from_blacklist(bot: Bot, user_id: int, callback_data: str):
    client_id = callback_data.split(":")[1]
    success = delete_blacklist_entry(int(client_id))
    if success:
        await bot.send_message(chat_id=user_id, text="User successfully removed from the blacklist.")
    else:
        await bot.send_message(chat_id=user_id, text="Something went wrong. Please try again.")

async def handle_add_pair_inline(bot: Bot, user_id:int, callback_data: str):
    #add_pair_inline:
    group_id = int(callback_data.split(":")[1])
    
    if has_group_pair(group_id):
        await bot.send_message(chat_id=user_id, text="this Group Has Already been Paired. Please Choose Another Group")
        return
    session = get_sessions_by_user_id(user_id)
    
    group_info = get_member_shipgroup_by_id(group_id)
    
    if session is not None and session.get("previous_data") is None:
        await bot.send_message(chat_id=user_id, text="now send me the username of the Second Group or add me to the group and send any message to the group or select from the above buttons")
        update_session(user_id, WAITING_FOR_SECOND_GROUP, group_info['group_data'])
        
    elif session is not None and session.get("previous_data") is not None:
        previoss_data = session.get("previous_data")
        if previoss_data.get("id") == group_id:
            await bot.send_message(chat_id=user_id, text="A group cant't be paired with itself. please choose another  Group")
            return
        create_group_pair(previoss_data, group_info['group_data'])
        await bot.send_message(chat_id=user_id, text=f"Pair created: {previoss_data['title']} <> {group_info['group_data']['title']} successfully.")
        update_session(user_id, None, None)
    
    else:
        await bot.send_message(chat_id=user_id, text="something went wrong!. please try again")
    