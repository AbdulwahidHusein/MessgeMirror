from .db import whitelist_collection
from typing import List, Dict

# Add a user to the whitelist (essentially, just create the user in the database)
def add_to_whitelist(userdata) -> bool:
    """
    Add a user to the whitelist by inserting or updating their data in the database.
    
    Arguments:
    userdata -- a dictionary containing user_id and other user-related information.
    
    Returns:
    True if the user was added or updated successfully, otherwise False.
    """
    user_id = userdata['id']
    result = whitelist_collection.update_one(
        {'user_id': user_id},  
        {'$set': {
            'user_id': user_id, 
            'user_data': userdata 
        }},
        upsert=True  # Insert the user if they don't exist, update if they do
    )
    
    return result.matched_count > 0 or result.upserted_id is not None

def add_to_whitelist_by_username(username:str):
    result = whitelist_collection.update_one(
        {'user_id': username},  
        {'$set': {
            'user_id': username
        }},
        upsert=True
    )
    return result.matched_count > 0 or result.upserted_id is not None

# Check if a user is in the whitelist (i.e., exists in the database)
def is_whitelisted(user_id) -> bool:
    """
    Check if a user is whitelisted by checking if they exist in the database.
    
    Arguments:
    user_id -- the ID of the user to check.
    
    Returns:
    True if the user exists, otherwise False.
    """
    result = whitelist_collection.find_one({'user_id': user_id})
    return result is not None 


# Get all whitelisted users (i.e., all users in the collection)
def get_whitelisted_users() -> List[Dict]:
    """
    Retrieve all whitelisted users from the database.
    
    Returns:
    A list of dictionaries representing whitelisted users.
    """
    users = whitelist_collection.find()  
    return list(users)  # Convert the cursor to a list of users


# Remove a user from the whitelist (i.e., delete their entry from the database)
def remove_from_whitelist(user_id) -> bool:
    """
    Remove a user from the whitelist by deleting their entry from the database.
    
    Arguments:
    user_id -- the ID of the user to remove.(it can be a username)
    
    Returns:
    True if a user was removed, otherwise False.
    """
    result = whitelist_collection.delete_one({'user_id': user_id}) 
    
    return result.deleted_count > 0   
