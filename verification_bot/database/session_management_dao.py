from datetime import datetime
from .db import user_session_collection

def create_session(user_id, session_name, previous_data):
    """Create a new session for a user if one doesn't exist."""

    new_session = {
        'user_id': user_id,
        'created_at': datetime.now(),
        'session_name': session_name,
        'previous_data': previous_data
    }
    user_session_collection.insert_one(new_session)
    return new_session


def update_session(user_id=None, session_name=None, previous_data=None):
    """Update an existing session for a user, or create a new one if it doesn't exist."""
    update_fields = {}
    if session_name is not None:
        update_fields['session_name'] = session_name
    if previous_data is not None:
        update_fields['previous_data'] = previous_data

    result = user_session_collection.update_one({'user_id': user_id}, {'$set': update_fields})

    if result.matched_count == 0:
        return create_session(user_id, session_name, previous_data)
    return result
    

def get_sessions_by_user_id(user_id) :
    session = get_session_from_db(user_id)
    if session is None:
        session = create_session(user_id, None, None)  
    return session

def get_session_from_db(user_id):
    session_data = user_session_collection.find_one({"user_id": user_id})  
    if session_data:
        return session_data
    return None



def delete_session(user_id):
    """Delete a user's session by user_id."""
    deletion_result = user_session_collection.delete_one({'user_id': user_id})
    
    return deletion_result