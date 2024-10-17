import asyncio
from datetime import datetime, timedelta
import pytz  
from telethon import TelegramClient
from config import Config

# Telegram API credentials
API_ID = Config.TELEGRAM_API_ID           
API_HASH = Config.TELEGRAM_API_HASH
PHONE_NUMBER = Config.TELEGRAM_PHONE_NUMBER

async def fetch_similar_messages(group_username, account_number, hours_back=3):
    messages = []
    # Using async with to manage the client session
    async with TelegramClient('session_name', API_ID, API_HASH) as client:
        # Get group entity and set timezone
        group = await client.get_entity(group_username)
        tz = pytz.UTC  
        cutoff_time = datetime.now(tz) - timedelta(hours=hours_back)

        async for message in client.iter_messages(group, search=account_number):
            # Set timezone for naive datetime objects
            if message.date.tzinfo is None:
                message.date = message.date.replace(tzinfo=tz)

            # Stop searching if the message is older than the cutoff time
            if message.date < cutoff_time:
                break

            messages.append(message)
    
    return messages

async def search_messages(group_username, account_number, hours_back=3):
    return await fetch_similar_messages(group_username, account_number, hours_back)

# Main entry point for testing
if __name__ == '__main__':
    async def main():
        result = await search_messages("@ababababnl", "67304733674")
        if result:
            print(result[0].text)
        else:
            print("No messages found.")

    asyncio.run(main())
