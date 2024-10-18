import asyncio
from datetime import datetime, timedelta
import pytz  
from telethon import TelegramClient
from config import Config
from .check_similarity import approximate_match


# Telegram API credentials
API_ID = Config.TELEGRAM_API_ID           
API_HASH = Config.TELEGRAM_API_HASH
PHONE_NUMBER = Config.TELEGRAM_PHONE_NUMBER

async def fetch_similar_messages(group_username, settlment_request, hours_back=30):
    messages = []
    # Using async with to manage the client session
    async with TelegramClient('session_name', API_ID, API_HASH) as client:
        # Get group entity and set timezon
            
        group = await client.get_entity(group_username)
        tz = pytz.UTC  
        cutoff_time = datetime.now(tz) - timedelta(hours=hours_back)

        async for message in client.iter_messages(group):
            # Set timezone for naive datetime objects
            if message.date.tzinfo is None:
                message.date = message.date.replace(tzinfo=tz)

            # Stop searching if the message is older than the cutoff time
            if message.date < cutoff_time:
                break
            if message.text and approximate_match(message.text, settlment_request):
                messages.append(message)
    
    return messages

async def search_messages(group_username, settlment_request, hours_back=3):
    return await fetch_similar_messages(group_username, settlment_request, hours_back)

# Main entry point for testing
if __name__ == '__main__':
    async def main():
        result = await search_messages("@ababababnl", "67304733674", 1000)
        if result:
            print(result[0].text)
        else:
            print("No messages found.") 

    asyncio.run(main())
