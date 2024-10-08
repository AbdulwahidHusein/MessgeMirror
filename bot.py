import os
from typing import Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel
import logging
from telegram import Bot, Message
from telegram.error import TelegramError

# Telegram Bot Token
Token = "7726243665:AAHgsI4RR2feW0Rotraru5V2_mJYe1dT170"
bot = Bot(Token)

# Group A and Group B IDs (replace these with actual group chat IDs)
GROUP_A_ID = -4561562870  # Replace with actual Group A ID
GROUP_B_ID = -4579233480  # Replace with actual Group B ID

# Initialize FastAPI app
app = FastAPI()
# Initialize FastAPI app


# Group A and Group B IDs (replace these with actual group chat IDs)
GROUP_A_ID = -1001234567890  # Replace with actual Group A ID
GROUP_B_ID = -1009876543210  # Replace with actual Group B ID

# Initialize FastAPI app
app = FastAPI()

# Configure logging to output all request details
logging.basicConfig(level=logging.INFO)

# Pydantic model for handling incoming webhook data
class TelegramWebhook(BaseModel):
    '''
    Telegram Webhook Model using Pydantic for request body validation
    '''
    update_id: int
    message: Optional[dict] = None


@app.post("/webhook")
async def webhook(webhook_data: TelegramWebhook):
    if webhook_data.message:
        print(webhook_data.message)
        # Extract message information
        message = webhook_data.message
        chat_id = message['chat']['id']
        text = message.get('text')
        reply_to_message = message.get('reply_to_message')
        photo = message.get('photo')  # For handling photo messages
        document = message.get('document')  # For handling document messages
        video = message.get('video')  # For handling video messages
        caption = message.get('caption')  # Caption for media
        message_id = message['message_id']
        
        try:
            # If the message is from Group A, forward to Group B
            if chat_id == GROUP_A_ID:
                await forward_message(GROUP_B_ID, text, photo, document, video, caption, reply_to_message)

            # If the message is from Group B, forward to Group A
            elif chat_id == GROUP_B_ID:
                await forward_message(GROUP_A_ID, text, photo, document, video, caption, reply_to_message)

        except TelegramError as e:
            logging.error(f"Telegram API error: {e}")

    return {"message": "ok"}


async def forward_message(target_group_id: int, text: Optional[str], photo: Optional[list], 
                          document: Optional[dict], video: Optional[dict], caption: Optional[str], 
                          reply_to_message: Optional[dict]):
    """
    Forwards messages, handles text, replies, and media (photos, videos, documents).
    """
    try:
        # Handle text messages
        if text:
            if reply_to_message:
                original_text = reply_to_message.get('text', 'Message')
                text = f"Reply to: {original_text}\n{text}"
            await bot.send_message(chat_id=target_group_id, text=text)

        # Handle photo messages
        elif photo:
            largest_photo = photo[-1]['file_id']  # The largest version of the photo
            await bot.send_photo(chat_id=target_group_id, photo=largest_photo, caption=caption)

        # Handle document messages
        elif document:
            file_id = document['file_id']
            await bot.send_document(chat_id=target_group_id, document=file_id, caption=caption)

        # Handle video messages
        elif video:
            file_id = video['file_id']
            await bot.send_video(chat_id=target_group_id, video=file_id, caption=caption)

    except TelegramError as e:
        logging.error(f"Failed to forward message: {e}")


@app.get("/")
def index():
    return {"message": "Hello World"}