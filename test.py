import os
from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext


# Load environment variables
load_dotenv()


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
    update_session
)


WAITING_FOR_FIRST_GROUP = "waiting_for_first_group"
WAITING_FOR_SECOND_GROUP = "waiting_for_second_group"
WAITING_FOR_PAIR_SAVE = "waiting_for_save"

WAITING_FOR_GROUP_DELETE_SELECTION = "waiting_for_group_selection"
WAITING_FOR_GROUP_DELETE_CONFIRM = "waiting_for_confirm"

WAITING_FOR_BLACKLIST_USER = "waiting_for_blacklist_user"
WAITING_FOR_BLACKLIST_CONFIRM = "waiting_for_blacklist_confirm"

WAITING_FOR_REMOVE_BLACKLIST_USER = "waiting_for_remove_blacklist_user"
WAITING_FOR_REMOVE_BLACKLIST_CONFIRM = "waiting_for_remove_blacklist_confirm"

class UserSession:
    def __init__(self,userid,  session_name):
        self.userid = userid
        self.session_name = session_name




class SessionManager:
    def __init__(self, bot: Bot, update_message):
        self.bot = bot
        self.update_message = update_message
        self.from_id = update_message['from']['id']
        
        self.user_session = get_sessions_by_user_id(self.from_id)
        
        if not self.user_session:
            self.user_session = create_session(self.from_id, None)
        
    async def handle_message(self):
        text = self.update_message['text']
        
        print("text:             t", text)
        if text == '/start':
            self.start()
        
        elif text == 'Add Pair':
            await self.handle_add_pair()
        
        elif text == 'Remove Pair':
            await self.handle_remove_pair()
        
        elif text == 'Add to Blacklist':
            pass
        
        elif text == 'Remove From Black list':
            pass
        
        elif text == 'Get Pairs':
            pass
        
        elif text == 'Get Blacklist':
            pass
        
        else:
            await self.bot.send_message(chat_id=self.from_id, text="Unknown command. Type /help for available commands.")
        
    
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
        await self.bot.send_message(chat_id=self.from_id, text="Please Forward a message from the first Guoup")
        update_session(self.from_id, WAITING_FOR_FIRST_GROUP)
        
    async def handle_remove_pair(self):
        pairs = get_group_pairs()
        
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No pairs found.")
            return

        # Create the list of buttons for the inline keyboard
        keyboards = []
        for pair in pairs:
            keyboards.append([InlineKeyboardButton(pair["group1_id"], callback_data=f"remove_pair:{pair['group1_id']}")])
        
        # Create the inline keyboard markup using the list of buttons
        reply_markup = InlineKeyboardMarkup(keyboards)

        # Send the message with the inline keyboard
        await self.bot.send_message(chat_id=self.from_id, text="Select a pair to remove:", reply_markup=reply_markup)
        
        update_session(self.from_id, WAITING_FOR_GROUP_DELETE_SELECTION)
        
async def handle_add_to_blacklist(self):
    await self.bot.send_message(chat_id=self.from_id, text="Forward be a message from The user to be blacklisted")
    update_session(self.from_id, WAITING_FOR_BLACKLIST_USER)