import os
from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from utils import *
from states import *
from message_handler import CommonMessageHandler
# Load environment variables
load_dotenv()

from model import TelegramWebhook

# Import your MongoDB operations here
from mongo import (
    create_group_pair,
    get_group_pairs,
    delete_group_pair,
    create_blacklist_entry,
    get_blacklist,
    delete_blacklist_entry,
    create_session,
    get_sessions_by_user_id,
    delete_session,
    update_session,
    delete_session,
    has_group_pair
)




class UserSession:
    def __init__(self,userid,  session_name):
        self.userid = userid
        self.session_name = session_name




class SessionManager:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        update_message = webhook_data.message
        self.bot = bot
        self.update_message = update_message
        self.from_id = update_message['from']['id']
    
        self.user_session = get_sessions_by_user_id(self.from_id)
        
        self.webhook_data = webhook_data
        
        self.message_handler = CommonMessageHandler(bot, webhook_data)
        
        
    async def handle_message(self):
        text = self.update_message['text']
        
        if text == '/start':
            await self.start()
        
        elif text == 'Add Pair':
            await self.handle_add_pair()
        
        elif text == 'Remove Pair':
            await self.handle_remove_pair()
        
        elif text == 'Add to Blacklist':
            await self.handle_add_to_blacklist()
        
        elif text == 'Remove From Black list':
            await self.handle_remove_from_blacklist()
        
        elif text == 'Get Pairs':
            await self.handle_get_pairs()
        
        elif text == 'Get Blacklist':
            await self.handle_get_blacklist()
        
        else:
            await self.message_handler.handle_messages()
            # await self.bot.send_message(chat_id=self.from_id, text="Unknown command. Type /help for available commands.")
        
    
    async def start(self):
        
        await self.bot.send_message(
            chat_id=self.from_id,
            text="Select an option:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    ["Add Pair", "Remove Pair"],
                    ["Add to Blacklist", "Remove From Black list"],
                    ["Get Pairs", "Get Blacklist"],
                    ["Help", "Exit"],
                ],
                one_time_keyboard=False ,
                resize_keyboard=True
            )
        )
        
        
    async def handle_add_pair(self):
        await self.bot.send_message(chat_id=self.from_id, text="Please send me username of the First Group")
        update_session(self.from_id, WAITING_FOR_FIRST_GROUP, None)
        
    async def handle_remove_pair(self):
        pairs = get_group_pairs()
        
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No pairs found.")
            return

        # Create the list of buttons for the inline keyboard
        keyboards = []
        for pair in pairs:
            keyboards.append([InlineKeyboardButton(text=f"{pair['group1_data']['title']} <> {pair['group2_data']['title']}", callback_data=f"remove_pair:{pair['group1_data']['id']}")])
        
        # Create the inline keyboard markup using the list of buttons
        reply_markup = InlineKeyboardMarkup(keyboards)

        # Send the message with the inline keyboard
        await self.bot.send_message(chat_id=self.from_id, reply_markup=reply_markup, text="Select a pair to remove:")
        
        
    async def handle_add_to_blacklist(self):
        await self.bot.send_message(chat_id=self.from_id, text="Forward be a message from The user to be blacklisted")
        update_session(self.from_id, WAITING_FOR_BLACKLIST_USER)
        
    async def handle_get_pairs(self):
        pairs = get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No pairs found.")
            return
        keyboards = [] 
        for pair in pairs:
            
            group1_title = pair.get("group1_data", {}).get('title', 'Unknown Group 1')
            group2_title = pair.get("group2_data", {}).get('title', 'Unknown Group 2')
            
            # Create button text
            button_text = f"{group1_title} <> {group2_title}"
            
            if button_text.strip():  
                keyboards.append([InlineKeyboardButton(text=button_text, callback_data='some_callback_data')])
            else:
                print("Button text is invalid, skipping...")

        # Create the InlineKeyboardMarkup
        reply_markup = InlineKeyboardMarkup(keyboards)
        
        await self.bot.send_message(chat_id=self.from_id, text="List of Group Pairs:", reply_markup=reply_markup)
        

        
    async def handle_remove_from_blacklist(self):
        
        blacklists = get_blacklist()
        keyboards =  []
        
        for blacklist in blacklists:
            button_text = ""
            if "first_name" in blacklist and blacklist["first_name"] is not None:
                button_text += blacklist["first_name"]
            
            if "last_name" in blacklist and blacklist["last_name"] is not None:
                botton_text += " " + blacklist["last_name"]
            if len(button_text.strip()) == 0:
                button_text = str ( blacklist['userid'])
            keyboards.append([InlineKeyboardButton(text=(button_text), callback_data=f"remove_from_blacklist:{blacklist['userid']}")])
            
        if not keyboards:
            await self.bot.send_message(chat_id=self.from_id, text="No blacklist found.")
            return
        
        reply_markup = InlineKeyboardMarkup(keyboards)
        
        await self.bot.send_message(chat_id=self.from_id, text="Select a user to remove from blacklist:", reply_markup=reply_markup)
        
        update_session(self.from_id, WAITING_FOR_REMOVE_BLACKLIST_USER, None)
        
    async def handle_get_blacklist(self): 
        blacklisted_users = get_blacklist()
        
        if len(blacklisted_users) == 0:
            await self.bot.send_message(chat_id=self.from_id, text="No Black listed Users Use the bottons to Blacklist users")
            return    
        keyboards = []
        
        for user in blacklisted_users:
            button_text = ""
            if "first_name" in user and user["first_name"] is not None:
                button_text += user["first_name"]

            if "last_name" in user and user["last_name"] is not None:
                button_text += " " + user["last_name"]

            if "username" in user and user["username"] is not None:
                button_text += " +@" + user["username"]

            if len(button_text.strip()) == 0: 
                button_text = user.get("userid", "Unknown User") 
            keyboards.append([InlineKeyboardButton(text=button_text, callback_data=f"action-on-user:{user['userid']}")])
        reply_markup = InlineKeyboardMarkup(keyboards)
        
        await self.bot.send_message(chat_id=self.from_id, text="List of Blacklisted  Users:", reply_markup=reply_markup)
if __name__ == "__main__":
    # Call the function directly
    get_group_info_by_username("Astuclassic45")