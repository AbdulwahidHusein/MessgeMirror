
from states import *
from mongo import *
from utils import *
from telegram import Bot

class CommonMessageHandler:
    def __init__(self, bot: Bot, update_message):
        self.bot = bot
        self.update_message = update_message
        self.from_id = update_message['from']['id']
    
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
            
            # Clear the session after successful creation
            delete_session(self.from_id)
            return
        
        elif session_name == WAITING_FOR_GROUP_DELETE_SELECTION:
            print(message)
