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
def create_group_pair(group1_id, group2_id):
    return group_pair_collection.insert_one({'group1_id': group1_id, 'group2_id': group2_id})

# Read
def get_group_pairs():
    return list(group_pair_collection.find())



# Delete
def delete_group_pair(group1_id, group2_id):
    return group_pair_collection.delete_one({
        'group1_id': group1_id,
        'group2_id': group2_id
    })



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
def create_blacklist_entry(userid):
    return blacklist_collection.insert_one({'userid': userid})

# Read
def get_blacklist():
    return list(blacklist_collection.find())

# Delete
def delete_blacklist_entry(userid):
    return blacklist_collection.delete_one({'userid': userid})


session_collection = db['Session']

# Create
def create_session(user_id, session_name):
    session_collection.insert_one({
        'user_id': user_id,
        'created_at': datetime.now(),
        'session_name': session_name
    })
    
    added_session = session_collection.find_one({'user_id': user_id})
    return added_session



# Update
def update_session( user_id=None, session_name=None):
    update_fields = {}
    if session_name is not None:
        update_fields['session_name'] = session_name
    return session_collection.update_one({'userid': user_id}, {'$set': update_fields})

def get_sessions_by_user_id(user_id):
    return list(session_collection.find({'user_id': user_id}))

# Delete
def delete_session(userid):
    return session_collection.delete_one({'userid': userid})


