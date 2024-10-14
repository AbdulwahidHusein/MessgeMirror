import asyncio
from datetime import datetime, timedelta
import pytz  
from telethon import TelegramClient
from config import Config

API_ID = Config.TELEGRAM_API_ID           
API_HASH = Config.TELEGRAM_API_HASH
PHONE_NUMBER = Config.TELEGRAM_PHONE_NUMBER
GROUP_NAME = '@astuwoch'   
HOURS_BACK = 3                

# Create the Telegram client
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    await client.start(phone=PHONE_NUMBER)  

    # Get the group
    group = await client.get_entity(GROUP_NAME)
    tz = pytz.UTC  

    # Calculate the cutoff time with timezone
    cutoff_time = datetime.now(tz) - timedelta(hours=HOURS_BACK)

    # List to hold messages
    messages_list = []

    # Retrieve and print past messages
    async for message in client.iter_messages(group):
        # Ensure message.date is aware (it should be, but this is to make sure)
        if message.date.tzinfo is None:
            message.date = message.date.replace(tzinfo=tz)  # Set timezone if naive

        # Stop if the message is older than the cutoff time
        if message.date < cutoff_time:
            break
        
        messages_list.append(f"[{message.date}] {message.sender_id}: {message.text}")

    return messages_list  

def run_bot():
    loop = asyncio.get_event_loop()
    messages = loop.run_until_complete(main())
    return messages

if __name__ == '__main__':
    result = run_bot()
    for msg in result:
        print(msg)
