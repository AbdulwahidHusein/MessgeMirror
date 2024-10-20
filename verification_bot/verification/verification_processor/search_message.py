from verification_bot.database import group_messages_dao
from .check_similarity import approximate_match



async def search(group_id, settlment_request, hours_back=30):
    messages = group_messages_dao.get_messages_from_hours_back(group_id)
    
    potential_messages = []
    for message in messages:
        if message['text'] and approximate_match(message['text'], settlment_request, 70):
            potential_messages.append(message)
    
    return potential_messages