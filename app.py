import os
from dotenv import load_dotenv
from typing import Optional

from fastapi import FastAPI
import logging
from telegram import Bot
from telegram.error import TelegramError
from private_bot import SessionManager
import call_back_queries
from model import TelegramWebhook
# Telegram Bot Token

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URL = os.getenv('MONGO_URL')
bot = Bot(BOT_TOKEN)


GROUP_A_ID = -4561562870  # Replace with actual Group A ID
GROUP_B_ID = -4579233480  # Replace with actual Group B ID


app = FastAPI()
logging.basicConfig(level=logging.INFO)
target_group_id = None



@app.post("/webhook")
async def webhook(webhook_data: TelegramWebhook):
    #handle group messages
    if webhook_data.message and webhook_data.message['chat']['type'] == "group":
        await process_message(webhook_data.message) 
    
    #handle private messages
    elif webhook_data.message and webhook_data.message['chat']['type'] == "private":
        session_manager = SessionManager(bot, webhook_data)
        await session_manager.handle_message()
    
    #handler callbacks
    elif webhook_data.callback_query:
        await call_back_queries.handle_callback_query(bot, webhook_data)

    #returns 200 status code to telegram
    return {"message": "ok"}


async def process_message(message: dict):
    """
    Process the incoming message and forward it to the appropriate group.
    """
    chat_id = message['chat']['id'] 
    target_group_id = get_target_group_id(chat_id)

    if target_group_id:
        await forward_message(target_group_id, message)


def get_target_group_id(chat_id: int) -> Optional[int]:
    """
    Determine the target group ID based on the incoming chat ID.
    """
    if chat_id == GROUP_A_ID:
        return GROUP_B_ID
    elif chat_id == GROUP_B_ID:
        return GROUP_A_ID
    return None


class Forwarder:
    def __init__(self, bot, webhook_data: TelegramWebhook):
        self.bot = bot
        self.webhook_data = webhook_data
        self.message = webhook_data.message
        
        
    def get_pair_group(self):
        return get_target_group_id(self.message['chat']['id'])
    
    async def handle_text_forward(self):
        target_group_id = self.get_pair_group()
        
        if "reply_to" in self.message:
            pass
        else:
            await bot.send_message(chat_id=target_group_id, text=self.message['text'])
    
    async def handle_media_forward(self):
        try:
            target_group_id = self.get_pair_group()
            if 'photo' in self.message:
                largest_photo = self.message['photo'][-1]['file_id']
                caption = self.message.get('caption', None)
                await bot.send_photo(chat_id=target_group_id, photo=largest_photo, caption=caption)

            # Handle video self.messages
            if 'video' in self.message:
                video = self.message['video']
                await bot.send_video(chat_id=target_group_id, video=video['file_id'], caption=self.message.get('caption', None),
                                    duration=video.get('duration'), width=video.get('width'), height=video.get('height'))

            # Handle document self.messages (like PDFs, files)
            if 'document' in self.message:
                document = self.message['document']
                await bot.send_document(chat_id=target_group_id, document=document['file_id'], caption=self.message.get('caption', None),
                                        filename=document.get('file_name'))

            # Handle audio self.messages
            if 'audio' in self.message:
                audio = self.message['audio']
                await bot.send_audio(chat_id=target_group_id, audio=audio['file_id'], caption=self.message.get('caption', None),
                                    duration=audio.get('duration'))

            # Handle voice self.messages
            if 'voice' in self.message:
                voice = self.message['voice']
                await bot.send_voice(chat_id=target_group_id, voice=voice['file_id'], duration=voice.get('duration'))

            # Handle animation (GIF) self.messages
            if 'animation' in self.message:
                animation = self.message['animation']
                await bot.send_animation(chat_id=target_group_id, animation=animation['file_id'], caption=self.message.get('caption', None))

            # Handle stickers
            if 'sticker' in self.message:
                sticker = self.message['sticker']
                await bot.send_sticker(chat_id=target_group_id, sticker=sticker['file_id'])

            # Handle locations
            if 'location' in self.message:
                location = self.message['location']
                await bot.send_location(chat_id=target_group_id, latitude=location['latitude'], longitude=location['longitude'])

            # Handle venues (detailed locations)
            if 'venue' in self.message:
                venue = self.message['venue']
                await bot.send_venue(chat_id=target_group_id, latitude=venue['location']['latitude'], longitude=venue['location']['longitude'],
                                    title=venue['title'], address=venue['address'])

            # Handle contacts
            if 'contact' in self.message:
                contact = self.message['contact']
                await bot.send_contact(chat_id=target_group_id, phone_number=contact['phone_number'], first_name=contact['first_name'])

            # Handle polls
            if 'poll' in self.message:
                poll = self.message['poll']
                options = [option['text'] for option in poll['options']]
                await bot.send_poll(chat_id=target_group_id, question=poll['question'], options=options)

            # Handle video notes (circular videos)
            if 'video_note' in self.message:
                video_note = self.message['video_note']
                await bot.send_video_note(chat_id=target_group_id, video_note=video_note['file_id'], duration=video_note.get('duration'))

        except TelegramError as e:
            print(e)
    
    

async def forward_message(target_group_id: int, message: dict):
    """
    Forward the message to the target group, handling different message types.
    """
    try:
        if 'text' in message:
            # Check if the message is a reply
            if 'reply_to_message' in message:
                reply_to_message = message['reply_to_message']
                if "text" in reply_to_message:  
                    original_message_preview = reply_to_message['text'][:50]  # Get the first 50 characters of the original message
                else:
                    original_message_preview = ""  # If the original message is not a text message, use "Message"
                reply_message = (
                    f"*🔄 {reply_to_message['from']['first_name']}*:\n"
                    f"{original_message_preview}...\n\n"  # Original message preview with ellipsis
                    f"{message['text']}"  # Current message
                )

                # Send formatted reply message
                await bot.send_message(
                    chat_id=target_group_id,
                    text=reply_message,
                    parse_mode='Markdown'  # Use Markdown for formatting
                )
            else:
                # If it's not a reply, just send the original message text
                await bot.send_message(chat_id=target_group_id, text=message['text'])


        # Handle photo messages
        if 'photo' in message:
            largest_photo = message['photo'][-1]['file_id']
            caption = message.get('caption', None)
            await bot.send_photo(chat_id=target_group_id, photo=largest_photo, caption=caption)

        # Handle video messages
        if 'video' in message:
            video = message['video']
            await bot.send_video(chat_id=target_group_id, video=video['file_id'], caption=message.get('caption', None),
                                 duration=video.get('duration'), width=video.get('width'), height=video.get('height'))

        # Handle document messages (like PDFs, files)
        if 'document' in message:
            document = message['document']
            await bot.send_document(chat_id=target_group_id, document=document['file_id'], caption=message.get('caption', None),
                                    filename=document.get('file_name'))

        # Handle audio messages
        if 'audio' in message:
            audio = message['audio']
            await bot.send_audio(chat_id=target_group_id, audio=audio['file_id'], caption=message.get('caption', None),
                                 duration=audio.get('duration'))

        # Handle voice messages
        if 'voice' in message:
            voice = message['voice']
            await bot.send_voice(chat_id=target_group_id, voice=voice['file_id'], duration=voice.get('duration'))

        # Handle animation (GIF) messages
        if 'animation' in message:
            animation = message['animation']
            await bot.send_animation(chat_id=target_group_id, animation=animation['file_id'], caption=message.get('caption', None))

        # Handle stickers
        if 'sticker' in message:
            sticker = message['sticker']
            await bot.send_sticker(chat_id=target_group_id, sticker=sticker['file_id'])

        # Handle locations
        if 'location' in message:
            location = message['location']
            await bot.send_location(chat_id=target_group_id, latitude=location['latitude'], longitude=location['longitude'])

        # Handle venues (detailed locations)
        if 'venue' in message:
            venue = message['venue']
            await bot.send_venue(chat_id=target_group_id, latitude=venue['location']['latitude'], longitude=venue['location']['longitude'],
                                 title=venue['title'], address=venue['address'])

        # Handle contacts
        if 'contact' in message:
            contact = message['contact']
            await bot.send_contact(chat_id=target_group_id, phone_number=contact['phone_number'], first_name=contact['first_name'])

        # Handle polls
        if 'poll' in message:
            poll = message['poll']
            options = [option['text'] for option in poll['options']]
            await bot.send_poll(chat_id=target_group_id, question=poll['question'], options=options)

        # Handle video notes (circular videos)
        if 'video_note' in message:
            video_note = message['video_note']
            await bot.send_video_note(chat_id=target_group_id, video_note=video_note['file_id'], duration=video_note.get('duration'))


    except TelegramError as e:
        print(e)
        



@app.get("/")
def index():
    return {"message": "Hello World"}
