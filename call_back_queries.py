from telegram import Bot
from model import TelegramWebhook
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ReplyKeyboardMarkup

from mongo import delete_group_pair, delete_blacklist_entry

async def handle_callback_query(bot: Bot, webhook_data: TelegramWebhook):
    callback_query = webhook_data.callback_query
    user_id = callback_query['from']['id']
    callback_data = callback_query['data']
    
    message = callback_query.get('message', {})
    
    
    print(f"Callback query received: {callback_query}")

    if callback_data.startswith("remove_pair:"):
        pair_id = callback_data.split(":")[1]
        
        await bot.send_message(chat_id=user_id, text=f"are You Sure?.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Yes", callback_data=f"confirm_remove_pair:{pair_id}"), InlineKeyboardButton(text="No", callback_data="cancel")]
        ]))
    
    elif callback_data.startswith("confirm_remove_pair:"):
        pair_id = callback_data.split(":")[1]
        success = delete_group_pair(int(pair_id))
        if success:
            await bot.send_message(chat_id=user_id, text=f"Successfully removed the pair: {pair_id}.")
        else:
            await bot.send_message(chat_id=user_id, text=f"Failed to remove the pair: {pair_id}.")
            
    elif callback_data.startswith("remove_from_blacklist:"):
        client_id = callback_data.split(":")[1]
        success = delete_blacklist_entry(int(client_id))
        
        if success:
            await bot.send_message(chat_id=user_id, text=f"User Successfully removed the Blacklist:.")
        else:
            await bot.send_message(chat_id=user_id, text="Something went wrong please try again")
    else:
        await bot.send_message(chat_id=user_id, text="Unknown action. Please try again.")
        


# def handle_delete_pair(user_id: int, pair_id: str, bot:Bot):