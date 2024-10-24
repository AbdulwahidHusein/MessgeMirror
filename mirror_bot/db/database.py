from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from models import LRUCache
from config import Config
import logging

MONGO_URL = Config.MONGO_URL
client = MongoClient(MONGO_URL)
db = client['messagemerror']

# Collections
group_pair_collection = db['GroupPair']
message_pair_collection = db['MessagePair']
whitelist_collection = db['Whitelist']
session_collection = db['Session']
member_ship_collection = db['MemberShip']


config_collection = db['Config']



# Initialize LRU Caches
session_cache = LRUCache(capacity=100)
whitelist_cache = LRUCache(capacity=100)
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
        'forwarded_id': forwarded_id,
        'created_at': datetime.now(timezone.utc)  # Store in UTC

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
# whitelist Management
# =======================================
def create_whitelist_entry(userid, first_name=None, last_name=None, username=None):
    """Add a user to the whitelist."""
    whitelist_entry = {
        'userid': userid,
        'first_name': first_name,
        'last_name': last_name,
        'username': username
    }
    
    whitelist_collection.insert_one(whitelist_entry)
    whitelist_cache.put(userid, whitelist_entry)  # Cache the entry
    return whitelist_entry


def get_whitelist():
    """Retrieve the list of whitelisted users."""
    if len(whitelist_cache.cache) == 0:
        # Load from database if not in cache
        whitelisted_users = list(whitelist_collection.find())
        for user in whitelisted_users:
            whitelist_cache.put(user['userid'], user)
    return list(whitelist_cache.cache.values())


def delete_whitelist_entry(userid):
    """Remove a user from the whitelist."""
    deletion_result = whitelist_collection.delete_one({'userid': userid})
    if deletion_result.deleted_count > 0:
        # Remove from cache if found
        whitelist_cache.cache.pop(userid, None)
    return deletion_result


def is_whitelisted(userid):
    """Check if a user is whitelisted."""
    if whitelist_cache.get(userid) is not None:
        return True
    return whitelist_collection.find_one({'userid': userid}) is not None


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


    current_session = session_cache.get(user_id)
    if current_session is None:
        current_session = {}  
    session_cache.put(user_id, {**current_session, **update_fields})

    return session_cache.get(user_id)



def get_sessions_by_user_id(user_id) :
    session = get_session_from_db(user_id)
    if session is None:
        session = create_session(user_id, None, None)  
    return session

def get_session_from_db(user_id):
    session_data = session_collection.find_one({"user_id": user_id})  
    if session_data:
        return session_data
    return None



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
    
    membership_cache.put(group_id, {"group_data": group_info})
    return result.upserted_id


def delete_member_ship(group_id: int):
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


def get_member_shipgroup_by_id(group_id: int):
    """Retrieve a membership group by its group_id."""
    group = membership_cache.get(group_id)
    if group is None:
        group = member_ship_collection.find_one({'id': group_id})
        if group:
            membership_cache.put(group_id, group)  # Cache the found group
    return group


def datetime_to_epoch_ms(dt):
    """Convert a datetime object to epoch milliseconds."""
    return int(dt.timestamp() * 1000)

from datetime import datetime, timedelta, timezone

def delete_old_message_pairs(before_days, from_group_id=None):
    """
    Delete message pairs for a given `from_group_id` that are older than a specified number of days.
    
    Args:
        from_group_id (int): The group ID from which messages are forwarded.
        before_days (int): The number of days before which messages should be deleted.
    
    Returns:
        int: The number of message pairs deleted.
    """
    # Get the current time in UTC
    now_utc = datetime.now(timezone.utc)

    # Define the cutoff date by subtracting `before_days` from the current date
    cutoff_date = now_utc - timedelta(days=before_days)

    # Prepare the query to match messages from `from_group_id` older than the cutoff date
    query = {'created_at': {'$lt': cutoff_date}}
    
    # Add the group ID filter if specified
    if from_group_id is not None:
        query['from_group_id'] = from_group_id

    # Check if documents match the query before deletion
    matching_documents_count = message_pair_collection.count_documents(query)
    
    if matching_documents_count == 0:
        # print("No matching documents found.")
        return 0
    
    # Perform the deletion and get the result
    deletion_result = message_pair_collection.delete_many(query)


    return deletion_result.deleted_count




service_cache = {}

def add_or_update_service(service_name: str, state: bool):
    result = config_collection.update_one(
        {"service_name": service_name},
        {"$set": {"is_enabled": state}},
        upsert=True
    )
    
    service_cache[service_name] = state
    
    if result.upserted_id:
        logging.info(f"Added new service: {service_name} with state: {state}")
    else:
        logging.info(f"Updated existing service: {service_name} with state: {state}")
    return True

def get_service_state(service_name: str) -> bool:
    if service_name in service_cache:
        logging.info(f"Cache hit for {service_name}.")
        return service_cache[service_name]
    

    logging.info(f"Cache miss for {service_name}.")
    service = config_collection.find_one({"service_name": service_name})
    
    if service:
        service_cache[service_name] = service["is_enabled"]
        return service["is_enabled"]
    else:
        logging.info(f"Service {service_name} not found in database.")
        service_cache[service_name] = True  # Default state is True
        return True


