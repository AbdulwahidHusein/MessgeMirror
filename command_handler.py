import os
from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, 
    ReplyKeyboardMarkup
)
from telegram.ext import CallbackContext
from utils import *
from states import *
from states_handler import CommonMessageHandler
from model import TelegramWebhook
from mongo import (
     get_group_pairs,  get_blacklist, get_sessions_by_user_id, update_session, delete_session, get_member_ship_groups
)

# Load environment variables
load_dotenv()

class UserSession:
    def __init__(self, user_id: int, session_name: str):
        self.user_id = user_id
        self.session_name = session_name

class SessionManager:
    def __init__(self, bot: Bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.update_message = webhook_data.message
        self.from_id = self.update_message['from']['id']
        self.user_session = get_sessions_by_user_id(self.from_id)
        self.webhook_data = webhook_data
        self.message_handler = CommonMessageHandler(bot, webhook_data)

    async def handle_message(self):
        text = self.update_message['text']
        handlers = {
            '/start': self.start,
            'Add Pair': self.handle_add_pair,
            'Remove Pair': self.handle_remove_pair,
            'Add to Blacklist': self.handle_add_to_blacklist,
            'Remove From Black list': self.handle_remove_from_blacklist,
            'Get Pairs': self.handle_get_pairs,
            'Get Blacklist': self.handle_get_blacklist,
            'Help': self.handle_help,
            'Exit': self.handle_exit,
        }
        
        handler = handlers.get(text)
        if handler:
            await handler()
        else:
            await self.message_handler.handle_messages()

    async def start(self):
        await self._send_message_with_keyboard(
            chat_id=self.from_id,
            text="Select an option:",
            options=[
                ["Add Pair", "Remove Pair"],
                ["Add to Blacklist", "Remove From Black list"],
                ["Get Pairs", "Get Blacklist"],
                ["Help", "Exit"]
            ]
        )

    async def handle_add_pair(self):
        membership_groups = get_member_ship_groups()
        
        await self.bot.send_message(chat_id=self.from_id, text="Please send me the username of the First Group or add me to the group and send any message to the group so that I can get the updates or use the below buttons to select from list of groups I am already member of")
        
        buttons = [[InlineKeyboardButton(text=f"{group["group_data"]['title']}", callback_data=f"add_pair_inline:{group["group_data"]['id']}")] for group in membership_groups]

        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a group to add:", buttons=buttons)
        update_session(self.from_id, WAITING_FOR_FIRST_GROUP, None)

    async def handle_remove_pair(self):
        pairs = get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No pairs found.")
            return

        buttons = [[InlineKeyboardButton(text=f"{pair['group1_data']['title']} <> {pair['group2_data']['title']}", callback_data=f"remove_pair:{pair['group1_data']['id']}")] for pair in pairs]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a pair to remove:", buttons=buttons)

    async def handle_add_to_blacklist(self):
        await self.bot.send_message(chat_id=self.from_id, text="Forward a message from the user to be blacklisted")
        update_session(self.from_id, WAITING_FOR_BLACKLIST_USER)

    async def handle_remove_from_blacklist(self):
        blacklists = get_blacklist()
        if not blacklists:
            await self.bot.send_message(chat_id=self.from_id, text="No blacklist found.")
            return

        buttons = [self._create_blacklist_button(user) for user in blacklists]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="Select a user to remove from the blacklist:", buttons=buttons)
        update_session(self.from_id, WAITING_FOR_REMOVE_BLACKLIST_USER, None)

    async def handle_get_pairs(self):
        pairs = get_group_pairs()
        if not pairs:
            await self.bot.send_message(chat_id=self.from_id, text="No pairs found.")
            return

        buttons = [self._create_group_pair_button(pair) for pair in pairs]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="List of Group Pairs:", buttons=buttons)

    async def handle_get_blacklist(self):
        blacklisted_users = get_blacklist()
        if not blacklisted_users:
            await self.bot.send_message(chat_id=self.from_id, text="No Blacklisted Users. Use the buttons to blacklist users.")
            return

        buttons = [self._create_blacklist_button(user) for user in blacklisted_users]
        await self._send_message_with_inline_keyboard(chat_id=self.from_id, text="List of Blacklisted Users:", buttons=buttons)

    async def handle_help(self):
        """Send a help message with a list of available commands."""
        help_message = """ 
                *Available Commands:*
                - /start: Start the bot and display options.
                - Add Pair: Add a pair of groups.
                - Remove Pair: Remove an existing group pair.
                - Add to Blacklist: Add a user to the blacklist.
                - Remove From Black list: Remove a user from the blacklist.
                - Get Pairs: List all group pairs.
                - Get Blacklist: List all blacklisted users.
                - Help: Display this help message.
                - Exit: Exit the bot.
                """
        await self.bot.send_message(chat_id=self.from_id, text=help_message, parse_mode='Markdown')

    async def handle_exit(self):
        """Handle the exit command by resetting the session and sending an exit message."""
        await self.bot.send_message(chat_id=self.from_id, text="Your session has ended.")
        delete_session(self.from_id)

    async def _send_message_with_keyboard(self, chat_id: int, text: str, options: list):
        """Helper method to send a message with a custom reply keyboard."""
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=options,
                one_time_keyboard=False,
                resize_keyboard=True
            )
        )

    async def _send_message_with_inline_keyboard(self, chat_id: int, text: str, buttons: list):
        """Helper method to send a message with inline keyboard buttons."""
        reply_markup = InlineKeyboardMarkup(buttons)
        await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    def _create_blacklist_button(self, user: dict) -> list:
        """Helper method to create a button for each blacklisted user."""
        button_text = f"{user.get('first_name', '')} {user.get('last_name', '')} Press To Remove From Blacklist".strip() or str(user['userid'])
        return [InlineKeyboardButton(text=button_text, callback_data=f"remove_from_blacklist:{user['userid']}")]

    def _create_group_pair_button(self, pair: dict) -> list:
        """Helper method to create a button for each group pair."""
        group1_title = pair.get("group1_data", {}).get('title', 'Unknown Group 1')
        group2_title = pair.get("group2_data", {}).get('title', 'Unknown Group 2')
        button_text = f"{group1_title} <> {group2_title}"
        return [InlineKeyboardButton(text=button_text, callback_data='some_callback_data')]

  
