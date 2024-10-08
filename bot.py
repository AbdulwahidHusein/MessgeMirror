import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Bot
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(level=logging.INFO)

# Telegram Bot Token
TOKEN = "7726243665:AAHgsI4RR2feW0Rotraru5V2_mJYe1dT170"
bot = Bot(TOKEN)

# Group A and Group B IDs (replace these with actual group chat IDs)
GROUP_A_ID = -4561562870  # Replace with actual Group A ID
GROUP_B_ID = -4579233480  # Replace with actual Group B ID

# Initialize FastAPI app
app = FastAPI()


class TelegramWebhook(BaseModel):
    """
    Telegram Webhook Model using Pydantic for request body validation.
    """
    update_id: int
    message: Optional[dict] = None
    edited_message: Optional[dict] = None
    channel_post: Optional[dict] = None
    edited_channel_post: Optional[dict] = None
    inline_query: Optional[dict] = None
    chosen_inline_result: Optional[dict] = None
    callback_query: Optional[dict] = None
    shipping_query: Optional[dict] = None
    pre_checkout_query: Optional[dict] = None
    poll: Optional[dict] = None
    poll_answer: Optional[dict] = None


@app.post("/webhook")
async def webhook(webhook_data: TelegramWebhook):
    """
    Handle incoming webhook data from Telegram.
    """
    if webhook_data.message:
        await process_message(webhook_data.message)
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



async def forward_message(target_group_id: int, message: dict):
    """
    Forward the message to the target group, handling different message types.
    """
    try:
        if 'text' in message:
            await handle_text_message(target_group_id, message)
        if 'photo' in message:
            await handle_photo_message(target_group_id, message)
        if 'video' in message:
            await handle_video_message(target_group_id, message)
        if 'document' in message:
            await handle_document_message(target_group_id, message)
        if 'audio' in message:
            await handle_audio_message(target_group_id, message)
        if 'voice' in message:
            await handle_voice_message(target_group_id, message)
        if 'animation' in message:
            await handle_animation_message(target_group_id, message)
        if 'sticker' in message:
            await handle_sticker_message(target_group_id, message)
        if 'location' in message:
            await handle_location_message(target_group_id, message)
        if 'venue' in message:
            await handle_venue_message(target_group_id, message)
        if 'contact' in message:
            await handle_contact_message(target_group_id, message)
        if 'poll' in message:
            await handle_poll_message(target_group_id, message)
        if 'video_note' in message:
            await handle_video_note_message(target_group_id, message)

    except TelegramError as e:
        logging.error(f"Failed to forward message: {e}")


async def handle_text_message(target_group_id: int, message: dict):
    """
    Handle text messages and forward them appropriately.
    """
    if 'reply_to_message' in message:
        reply_to_message = message['reply_to_message']
        if "text" in reply_to_message:
            original_message_preview = reply_to_message['text'][:50]
        else:
            original_message_preview = ""
        reply_message = (
            f"*🔄 {reply_to_message['from']['first_name']}*:\n"
            f"{original_message_preview}...\n\n"
            f"{message['text']}"
        )
        await bot.send_message(
            chat_id=target_group_id,
            text=reply_message,
            parse_mode='Markdown'
        )
    else:
        await bot.send_message(chat_id=target_group_id, text=message['text'])


async def handle_photo_message(target_group_id: int, message: dict):
    """Handle and forward photo messages."""
    print(message["photo"])
    largest_photo = message['photo'][-1]['file_id']
    caption = message.get('caption', None)
    await bot.send_photo(chat_id=target_group_id, photo=largest_photo, caption=caption)


async def handle_video_message(target_group_id: int, message: dict):
    """Handle and forward video messages."""
    video = message['video']
    await bot.send_video(
        chat_id=target_group_id,
        video=video['file_id'],
        caption=message.get('caption', None),
        duration=video.get('duration'),
        width=video.get('width'),
        height=video.get('height')
    )


async def handle_document_message(target_group_id: int, message: dict):
    """Handle and forward document messages."""
    document = message['document']
    await bot.send_document(
        chat_id=target_group_id,
        document=document['file_id'],
        caption=message.get('caption', None),
        filename=document.get('file_name')
    )


async def handle_audio_message(target_group_id: int, message: dict):
    """Handle and forward audio messages."""
    audio = message['audio']
    await bot.send_audio(
        chat_id=target_group_id,
        audio=audio['file_id'],
        caption=message.get('caption', None),
        duration=audio.get('duration')
    )


async def handle_voice_message(target_group_id: int, message: dict):
    """Handle and forward voice messages."""
    voice = message['voice']
    await bot.send_voice(chat_id=target_group_id, voice=voice['file_id'], duration=voice.get('duration'))


async def handle_animation_message(target_group_id: int, message: dict):
    """Handle and forward animation messages."""
    animation = message['animation']
    await bot.send_animation(chat_id=target_group_id, animation=animation['file_id'], caption=message.get('caption', None))


async def handle_sticker_message(target_group_id: int, message: dict):
    """Handle and forward sticker messages."""
    sticker = message['sticker']
    await bot.send_sticker(chat_id=target_group_id, sticker=sticker['file_id'])


async def handle_location_message(target_group_id: int, message: dict):
    """Handle and forward location messages."""
    location = message['location']
    await bot.send_location(chat_id=target_group_id, latitude=location['latitude'], longitude=location['longitude'])


async def handle_venue_message(target_group_id: int, message: dict):
    """Handle and forward venue messages."""
    venue = message['venue']
    await bot.send_venue(
        chat_id=target_group_id,
        latitude=venue['location']['latitude'],
        longitude=venue['location']['longitude'],
        title=venue['title'],
        address=venue['address']
    )


async def handle_contact_message(target_group_id: int, message: dict):
    """Handle and forward contact messages."""
    contact = message['contact']
    await bot.send_contact(chat_id=target_group_id, phone_number=contact['phone_number'], first_name=contact['first_name'])


async def handle_poll_message(target_group_id: int, message: dict):
    """Handle and forward poll messages."""
    poll = message['poll']
    options = [option['text'] for option in poll['options']]
    await bot.send_poll(chat_id=target_group_id, question=poll['question'], options=options)


async def handle_video_note_message(target_group_id: int, message: dict):
    """Handle and forward video note messages."""
    video_note = message['video_note']
    await bot.send_video_note(chat_id=target_group_id, video_note=video_note['file_id'], duration=video_note.get('duration'))


@app.get("/")
def index():
    return {"message": "Hello World"}
