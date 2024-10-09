
from states import *
from mongo import *
from utils import *
from telegram import Bot
from model import TelegramWebhook

class CommonMessageHandler:
    def __init__(self, bot: Bot, webhook_data : TelegramWebhook):
        
        self.web_hook_data = webhook_data
        self.update_message = webhook_data.message
        self.bot = bot
  
        self.from_id = self.update_message['from']['id']
        self.user_session = get_sessions_by_user_id(self.from_id)
    
    
    async def handle_messages(self):
        message = self.update_message
        session_name = self.user_session["session_name"]
        previous_data = self.user_session["previous_data"]
        
        if session_name == WAITING_FOR_FIRST_GROUP:
            group_username = message['text']
            groupinfo = get_group_info_by_username(group_username)
            
            if not groupinfo or not groupinfo.get("ok"):
                await self.bot.send_message(chat_id=self.from_id, text="Invalid username. Please try again.")
                update_session(self.from_id, None, None)
                return
            if has_group_pair(groupinfo['result']["id"]):
                await self.bot.send_message(chat_id=self.from_id, text="Group pair already exists. Please try again.")
                update_session(self.from_id, None, None)
                return
            
            # Store first group data in session
            first_group_data = {
                "id": groupinfo['result']["id"],
                "title": groupinfo['result']["title"],
                "username": groupinfo['result']["username"]
            }
            
            update_session(self.from_id, WAITING_FOR_SECOND_GROUP, first_group_data)
            await self.bot.send_message(chat_id=self.from_id, text="Please send me the username of the Second Group")
        
        elif session_name == WAITING_FOR_SECOND_GROUP:
            if not previous_data:
                await self.bot.send_message(chat_id=self.from_id, text="Something went wrong, please try again.")
                update_session(self.from_id, None, None)
                return
            
            group_username = message['text']
            group2info = get_group_info_by_username(group_username)
            
            if not group2info or not group2info.get("ok"):
                await self.bot.send_message(chat_id=self.from_id, text="Invalid username. Please try again.")
                return
            
            if has_group_pair(group2info['result']["id"]):
                await self.bot.send_message(chat_id=self.from_id, text="Group pair already exists. Please try again.")
                return
            
            # Second group data
            second_group_data = {
                "id": group2info['result']["id"],
                "title": group2info['result']["title"], 
                "username": group2info['result']["username"]
            }
            
            # Ensure that the second group is not the same as the first group
            if second_group_data["id"] == previous_data["id"]:
                await self.bot.send_message(chat_id=self.from_id, text="You cannot pair a group with itself. Please send a different group.")
                return
            
            # Create the group pair
            create_group_pair(previous_data, second_group_data)
            await self.bot.send_message(chat_id=self.from_id, text= f"Pairs created {previous_data['title']} and {second_group_data['title']} successfully")
            update_session(self.from_id, None, None)
            return
        
        elif session_name == WAITING_FOR_BLACKLIST_USER:
            if "forward_origin" in message and message['forward_origin'] is not None:
                if "sender_user" in message["forward_origin"] and message['forward_origin'] is not None:
                    sender_user = message["forward_origin"]["sender_user"]
                    
                    user_id = sender_user["id"]
                    first_name = sender_user["first_name"]
                    
                    last_name = None
                    if "last_name" in sender_user:
                        last_name = sender_user["last_name"]
                    username = None
                    if "username" in sender_user:
                        username = message["from"]["username"]
                    
                    if is_blacklisted(user_id):
                        await self.bot.send_message(chat_id=self.from_id, text="User already blacklisted. forward message from other user")
                        return
                    success = create_blacklist_entry(user_id, first_name=first_name, last_name=last_name, username=username)
                    if not success:
                        await self.bot.send_message(chat_id=self.from_id, text="Something went wrong, please try again")
                        return
                    await self.bot.send_message(chat_id=self.from_id, text="User blacklisted successfully")
                    update_session(user_id, None, None)
                else:
                    await self.bot.send_message(text="This profile is Private I can't access Their Profile Please try sending Their username")
                    
            elif "text" in message and message['text'] is not None:
                await self.bot.send_message(chat_id=self.from_id, text="Please Froward Message from the user to be blacklisted")

