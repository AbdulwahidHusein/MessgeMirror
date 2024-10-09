
import requests
def get_group_info_by_username(username):
    if not username:
        return None
    if username[0] != "@":
        username = "@" + username
    
    if username[:6] == 'https:':
        if len(username) > 12:
            username = "@" + username[13:]
        else:
            return None
    
    # Define the URL
    url = f"https://api.telegram.org/bot7726243665:AAHgsI4RR2feW0Rotraru5V2_mJYe1dT170/getChat?chat_id={username}"
    
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