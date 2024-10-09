from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
load_dotenv()

# Connect to MongoDB
MONGO_URL = os.getenv('MONGO_URL')
client = MongoClient(MONGO_URL)
db = client['messagemerror']  


group_pair_collection = db['GroupPair']

# Create
def create_group_pair(group1_data, group2_data):
    return group_pair_collection.insert_one({'group2_data': group1_data, 'group1_data': group2_data})

def delete_group_pair(group_id):
    # Find the pair where either group1_data.id or group2_data.id matches the provided group_id
    result = group_pair_collection.find_one({
        '$or': [
            {'group1_data.id': group_id}, 
            {'group2_data.id': group_id}
        ]
    })

    if result:
        # If a matching pair is found, delete it
        deletion_result = group_pair_collection.delete_one({
            '$or': [
                {'group1_data.id': group_id}, 
                {'group2_data.id': group_id}
            ]
        })
        return deletion_result  # Return the result of the deletion operation
    else:
        # Return None if no pair was found to delete
        return None


# Read
def get_group_pairs():
    return list(group_pair_collection.find())



    
def has_group_pair(group_id):
    possibility1 = group_pair_collection.find_one({'group1_data.id': group_id})
    possibility2 = group_pair_collection.find_one({'group2_data.id': group_id})
    
    if possibility1 is not None:
        return possibility1
    elif possibility2 is not None:
        return possibility2
    else:
        return None

message_pair_collection = db['MessagePair']

# Create
def create_message_pair(from_group_id, to_group_id, original_id, forwarded_id):
    return message_pair_collection.insert_one({
        'from_group_id': from_group_id,
        'to_group_id': to_group_id,
        'original_id': original_id,
        'forwarded_id': forwarded_id
    })


# Delete
def delete_message_pair(pair_id):
    return message_pair_collection.delete_one({'_id': pair_id})


def get_forwarded_id(from_group_id, to_group_id, original_id):
    message_pair = message_pair_collection.find_one({
        'from_group_id': from_group_id,
        'to_group_id': to_group_id,
        'original_id': original_id
    })
    return message_pair['forwarded_id'] if message_pair else None


blacklist_collection = db['Blacklist']

# Create
def create_blacklist_entry(userid, first_name, last_name=None, username=None):
    return blacklist_collection.insert_one({'userid': userid, 'first_name': first_name, 'last_name': last_name, "username": username})

# Read
def get_blacklist():
    return list(blacklist_collection.find())

# Delete
def delete_blacklist_entry(userid):
    return blacklist_collection.delete_one({'userid': userid})

def is_blacklisted(userid):
    return blacklist_collection.find_one({'userid': userid}) is not None

session_collection = db['Session']
def create_session(user_id, session_name, previous_data):
    existing_session = session_collection.find_one({'user_id': user_id}) 
    if existing_session:
        return existing_session  # Do not create a new session if one exists

    session_collection.insert_one({
        'user_id': user_id,
        'created_at': datetime.now(),
        'session_name': session_name,
        'previous_data': previous_data
    })

    return session_collection.find_one({'user_id': user_id})

# Update
def update_session(user_id=None, session_name=None, previous_data=None):
    update_fields = {}
    if session_name is not None:
        update_fields['session_name'] = session_name
    if previous_data is not None:
        update_fields['previous_data'] = previous_data

    result = session_collection.update_one({'user_id': user_id}, {'$set': update_fields})

    # If no session existed, create one
    if result.matched_count == 0:
        return create_session(user_id, session_name, previous_data)

    return session_collection.find_one({'user_id': user_id})

# Get
def get_sessions_by_user_id(user_id):
    session = session_collection.find_one({'user_id': user_id})
    if session is None:
        # Create a new session if it does not exist
        return create_session(user_id, "default_session_name", "default_previous_data")
    return session

# Delete
def delete_session(user_id):
    return session_collection.delete_one({'user_id': user_id})