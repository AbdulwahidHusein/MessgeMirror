from pymongo import ASCENDING
from datetime import datetime, timedelta, timezone
from .db import group_message_collection

# Create an index on the "timestamp" field (done once, when initializing the module)
# group_message_collection.create_index([("timestamp", ASCENDING)])

def add_group_message(group_id, message: dict) -> bool:
    # Add group_id to the message
    message["group_id"] = group_id
    
    
    message["timestamp"] = datetime.now(timezone.utc)
    
    group_message_collection.insert_one(message)
    
    return True

def get_messages_by_chat_id(chat_id: int, limit: int = 500):
    """
    Retrieve messages by chat_id sorted by the most recent first.
    Default limit is set to 500.
    """
    messages = group_message_collection.find(
        {"group_id": chat_id}
    ).sort("timestamp", ASCENDING).limit(limit)
    
    return list(messages)

def get_messages_from_hours_back(chat_id: int, hours: int = 12, limit: int = 500):
    """
    Retrieve messages for a given chat_id within the last X hours, with an optional limit.
    Default limit is set to 500 messages.
    """
    # Calculate the time threshold based on the given number of hours back
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Query messages for the given group_id and within the time range, limited by the specified number
    messages = group_message_collection.find(
        {"group_id": chat_id, "timestamp": {"$gte": time_threshold}}
    ).sort("timestamp", ASCENDING).limit(limit)
    
    return list(messages)

