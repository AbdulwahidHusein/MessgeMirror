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
    query = {
        '$or': [
            {'group1_data.id': group_id},
            {'group2_data.id': group_id}
        ]
    }
    
    result = group_pair_collection.find_one(query)
    
    if result is not None:
        if result['group1_data']['id'] == group_id:
            return result['group2_data']['id']
        else:
            return result['group1_data']['id']
    else:
        return None 


message_pair_collection = db['MessagePair']

# Create
def create_message_pair(from_group_id, to_group_id, original_id, forwarded_id):
    
    
    result =  message_pair_collection.insert_one({
        'from_group_id': from_group_id,
        'to_group_id': to_group_id,
        'original_id': original_id,
        'forwarded_id': forwarded_id
    })
    return result


# Delete
def delete_message_pair(pair_id):
    return message_pair_collection.delete_one({'_id': pair_id})


def get_forwarded_id(from_group_id, to_group_id, original_id = None, forwarded_id = None):
    # print(from_group_id, to_group_id, original_id)
    filters = {
        'from_group_id': from_group_id,
        'to_group_id': to_group_id
    }
    
    if original_id is not None:
        filters['original_id'] = original_id
    if forwarded_id is not None:
        filters['forwarded_id'] = forwarded_id

    message_pair = message_pair_collection.find_one(filters)
    if forwarded_id is None:
        return message_pair['forwarded_id'] if message_pair else None
    else:
        return message_pair["original_id"] if message_pair else None

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
        return create_session(user_id, None, None)
    return session

# Delete
def delete_session(user_id):
    return session_collection.delete_one({'user_id': user_id})


member_ship_collection = db['MemberShip']



def create_member_ship(group_info: dict):
    group_id = group_info['id'] 

    result = member_ship_collection.update_one(
        {'id': group_id},
        {'$set': {'group_data': group_info}}, 
        upsert=True
    )
    
    return result.upserted_id  


def delete_member_ship(group_id: str):
    result = member_ship_collection.delete_one({'id': group_id}) 

    if result.deleted_count == 0:
        print(f"No document found with group_id: {group_id}")
        return None  
    return result.deleted_count

def get_member_ship_groups():
    return list(member_ship_collection.find())

def get_member_shipgroup_by_id(group_id: str):
    return member_ship_collection.find_one({'id': group_id})
