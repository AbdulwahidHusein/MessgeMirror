import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from model import LRUCache

# Load environment 
load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')
client = MongoClient(MONGO_URL)
db = client['messagemerror']

# Collections
group_pair_collection = db['GroupPair']
message_pair_collection = db['MessagePair']
blacklist_collection = db['Blacklist']
session_collection = db['Session']
member_ship_collection = db['MemberShip']



# Initialize LRU Caches
session_cache = LRUCache(capacity=100)
blacklist_cache = LRUCache(capacity=100)
membership_cache = LRUCache(capacity=100)

# =======================================
# Group Pair Management
# =======================================
def create_group_pair(group1_data, group2_data):
    """Insert a new group pair into the database."""
    return group_pair_collection.insert_one({'group1_data': group1_data, 'group2_data': group2_data})


def delete_group_pair(group_id):
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
def create_blacklist_entry(userid, first_name=None, last_name=None, username=None):
    """Add a user to the blacklist."""
    blacklist_entry = {
        'userid': userid,
        'first_name': first_name,
        'last_name': last_name,
        'username': username
    }
    
    blacklist_collection.insert_one(blacklist_entry)
    blacklist_cache.put(userid, blacklist_entry)  # Cache the entry
    return blacklist_entry


def get_blacklist():
    """Retrieve the list of blacklisted users."""
    if len(blacklist_cache.cache) == 0:
        # Load from database if not in cache
        blacklisted_users = list(blacklist_collection.find())
        for user in blacklisted_users:
            blacklist_cache.put(user['userid'], user)
    return list(blacklist_cache.cache.values())


def delete_blacklist_entry(userid):
    """Remove a user from the blacklist."""
    deletion_result = blacklist_collection.delete_one({'userid': userid})
    if deletion_result.deleted_count > 0:
        # Remove from cache if found
        blacklist_cache.cache.pop(userid, None)
    return deletion_result


def is_blacklisted(userid):
    """Check if a user is blacklisted."""
    if blacklist_cache.get(userid) is not None:
        return True
    return blacklist_collection.find_one({'userid': userid}) is not None


# =======================================
# Session Management
# =======================================
def create_session(user_id, session_name, previous_data):
    """Create a new session for a user if one doesn't exist."""
    existing_session = session_cache.get(user_id)
    if existing_session:
        return existing_session

    new_session = {
        'user_id': user_id,
        'created_at': datetime.now(),
        'session_name': session_name,
        'previous_data': previous_data
    }

    session_collection.insert_one(new_session)
    session_cache.put(user_id, new_session)  # Cache the new session
    return new_session


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
    
    # Update cache
    session_cache.put(user_id, {**session_cache.get(user_id), **update_fields})
    
    return session_cache.get(user_id)


def get_sessions_by_user_id(user_id):
    """Retrieve a user's session, or create a new one if none exists."""
    session = session_cache.get(user_id)
    if session is None:
        session = create_session(user_id, None, None)
    return session


def delete_session(user_id):
    """Delete a user's session by user_id."""
    deletion_result = session_collection.delete_one({'user_id': user_id})
    if deletion_result.deleted_count > 0:
        # Remove from cache
        session_cache.cache.pop(user_id, None)
    return deletion_result


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
    
    membership_cache.put(group_id, group_info)
    return result.upserted_id


def delete_member_ship(group_id: str):
    """Delete a membership group by its group_id."""
    result = member_ship_collection.delete_one({'id': group_id})
    if result.deleted_count > 0:
        # Remove from cache if found
        membership_cache.cache.pop(group_id, None)
    return result.deleted_count


def get_member_ship_groups():
    """Retrieve all membership groups."""
    if len(membership_cache.cache) == 0:
        membership_groups = list(member_ship_collection.find())
        for group in membership_groups:
            membership_cache.put(group['id'], group)
    return list(membership_cache.cache.values())


def get_member_shipgroup_by_id(group_id: str):
    """Retrieve a membership group by its group_id."""
    group = membership_cache.get(group_id)
    if group is None:
        group = member_ship_collection.find_one({'id': group_id})
        if group:
            membership_cache.put(group_id, group)  # Cache the found group
    return group
