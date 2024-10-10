import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv('MONGO_URL')
client = MongoClient(MONGO_URL)
db = client['messagemerror']

# Collections
group_pair_collection = db['GroupPair']
message_pair_collection = db['MessagePair']
blacklist_collection = db['Blacklist']
session_collection = db['Session']
member_ship_collection = db['MemberShip']

# =======================================
# Group Pair Management
# =======================================
def create_group_pair(group1_data, group2_data):
    """Insert a new group pair into the database."""
    return group_pair_collection.insert_one({'group1_data': group1_data, 'group2_data': group2_data})


def delete_group_pair(group_id):
    """
    Delete a group pair based on group_id.
    It deletes the pair if either group1_data.id or group2_data.id matches the provided group_id.
    """
    query = {'$or': [{'group1_data.id': group_id}, {'group2_data.id': group_id}]}
    result = group_pair_collection.find_one(query)

    if result:
        deletion_result = group_pair_collection.delete_one(query)
        return deletion_result
    return None  # Return None if no pair was found


def get_group_pairs():
    """Retrieve all group pairs from the database."""
    return list(group_pair_collection.find())


def has_group_pair(group_id):
    """Check if a group is part of an existing group pair."""
    query = {'$or': [{'group1_data.id': group_id}, {'group2_data.id': group_id}]}
    result = group_pair_collection.find_one(query)

    if result:
        if result['group1_data']['id'] == group_id:
            return result['group2_data']['id']
        return result['group1_data']['id']
    return None


# =======================================
# Message Pair Management
# =======================================
def create_message_pair(from_group_id, to_group_id, original_id, forwarded_id):
    """Create a new message pair between two groups."""
    return message_pair_collection.insert_one({
        'from_group_id': from_group_id,
        'to_group_id': to_group_id,
        'original_id': original_id,
        'forwarded_id': forwarded_id
    })


def delete_message_pair(pair_id):
    """Delete a message pair by its pair_id."""
    return message_pair_collection.delete_one({'_id': pair_id})


def get_forwarded_id(from_group_id, to_group_id, original_id=None, forwarded_id=None):
    """
    Retrieve the forwarded message ID based on the original message ID or vice versa.
    If forwarded_id is None, return the forwarded_id; otherwise, return the original_id.
    """
    filters = {'from_group_id': from_group_id, 'to_group_id': to_group_id}
    if original_id is not None:
        filters['original_id'] = original_id
    if forwarded_id is not None:
        filters['forwarded_id'] = forwarded_id

    message_pair = message_pair_collection.find_one(filters)
    if forwarded_id is None:
        return message_pair['forwarded_id'] if message_pair else None
    return message_pair['original_id'] if message_pair else None


# =======================================
# Blacklist Management
# =======================================
def create_blacklist_entry(userid, first_name, last_name=None, username=None):
    """Add a user to the blacklist."""
    return blacklist_collection.insert_one({
        'userid': userid, 'first_name': first_name, 'last_name': last_name, 'username': username
    })


def get_blacklist():
    """Retrieve the list of blacklisted users."""
    return list(blacklist_collection.find())


def delete_blacklist_entry(userid):
    """Remove a user from the blacklist."""
    return blacklist_collection.delete_one({'userid': userid})


def is_blacklisted(userid):
    """Check if a user is blacklisted."""
    return blacklist_collection.find_one({'userid': userid}) is not None


# =======================================
# Session Management
# =======================================
def create_session(user_id, session_name, previous_data):
    """
    Create a new session for a user if one doesn't exist.
    If the session exists, return the existing session.
    """
    existing_session = session_collection.find_one({'user_id': user_id})
    if existing_session:
        return existing_session

    session_collection.insert_one({
        'user_id': user_id,
        'created_at': datetime.now(),
        'session_name': session_name,
        'previous_data': previous_data
    })

    return session_collection.find_one({'user_id': user_id})


def update_session(user_id=None, session_name=None, previous_data=None):
    """Update an existing session for a user, or create a new one if it doesn't exist."""
    update_fields = {}
    if session_name is not None:
        update_fields['session_name'] = session_name
    if previous_data is not None:
        update_fields['previous_data'] = previous_data

    result = session_collection.update_one({'user_id': user_id}, {'$set': update_fields})

    if result.matched_count == 0:
        return create_session(user_id, session_name, previous_data)

    return session_collection.find_one({'user_id': user_id})


def get_sessions_by_user_id(user_id):
    """Retrieve a user's session, or create a new one if none exists."""
    session = session_collection.find_one({'user_id': user_id})
    if session is None:
        return create_session(user_id, None, None)
    return session


def delete_session(user_id):
    """Delete a user's session by user_id."""
    return session_collection.delete_one({'user_id': user_id})


# =======================================
# Membership Group Management
# =======================================
def create_member_ship(group_info: dict):
    """Add or update a membership group entry in the database."""
    group_id = group_info['id']
    result = member_ship_collection.update_one(
        {'id': group_id},
        {'$set': {'group_data': group_info}},
        upsert=True
    )
    return result.upserted_id


def delete_member_ship(group_id: str):
    """Delete a membership group by its group_id."""
    result = member_ship_collection.delete_one({'id': group_id})
    if result.deleted_count == 0:
        print(f"No document found with group_id: {group_id}")
        return None
    return result.deleted_count


def get_member_ship_groups():
    """Retrieve all membership groups."""
    return list(member_ship_collection.find())


def get_member_shipgroup_by_id(group_id: str):
    """Retrieve a membership group by its group_id."""
    return member_ship_collection.find_one({'id': group_id})
