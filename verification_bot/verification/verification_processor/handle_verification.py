from . import telegram_client
from .content_alignment import  verify_messages
from .parse_request import get_settlment_reqmodel

async def handle(message: dict, source_group_id: int) -> str:
    
    settlement_request = get_settlment_reqmodel(message['text'])
    
    similar_messages = await telegram_client.run_search(source_group_id, settlement_request.bank_account_number)
    
    # print(settlement_request)
    
    # ga_sender = message.from_user['username']
    # print(ga_message.from_user)
    print([a.text for a  in similar_messages])
    for ga_message in reversed(similar_messages):
        verified, idx = verify_messages(ga_message.text, settlement_request)
        
        if verified:  
            return (True, idx, similar_messages[:4], ga_message)
    
    return (False, -1, similar_messages[:4], None)