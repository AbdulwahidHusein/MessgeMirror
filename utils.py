import requests
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

def normalize_username(username: str) -> str:
    """Normalize the username to always start with @ and handle URLs."""
    if not username:
        return None

    # Handle full URL starting with https:// or http://
    if username.startswith(('https://t.me/', 'http://t.me/')):
        username = username.split('/')[-1]  # Extract the part after t.me/

    # Ensure the username starts with an @ symbol
    if not username.startswith('@'):
        username = '@' + username
    
    return username

def get_group_info_by_username(username: str):
    """Fetch group info from Telegram API by username, handling various formats."""
    username = normalize_username(username)
    if not username:
        return None

    # Define the URL for the Telegram API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={username}"

    # Make a synchronous HTTP GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        group_data = response.json()  # Convert response to JSON
        print(group_data)
        return group_data
    else:
        print(f"Failed to get group info: {response.status_code}")
        return None

if __name__ == "__main__":
    # Example usage with different formats
    print(get_group_info_by_username("https://t.me/jdbdbdbdhm"))
    print(get_group_info_by_username("@xcsdjsadf"))
    print(get_group_info_by_username("sdfndsfsd"))
