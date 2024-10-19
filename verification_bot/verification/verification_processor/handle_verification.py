import logging
from . import telegram_client
from .content_alignment import verify_messages
from .parse_request import get_settlement_request_model
from .models import HandleResponse
from verification_bot.database import whitelist_dao, settlement_request_dao
from . import response_types as response_types
from typing import Any


async def handle(message: dict, source_group_id: Any, source_group_title: str) -> HandleResponse:
    response = HandleResponse(status=response_types.NOT_VERIFIED)
    
    try:
        settlement_request = get_settlement_request_model(message['text'])


        if settlement_request and settlement_request.merchant_name.lower() not in source_group_title.lower():
            response.status = "merchant name not in group"
            return response
        
        similar_messages = await telegram_client.search_messages(source_group_id, settlement_request)
        

        response.similar_messages = similar_messages

        for ga_message in similar_messages:
            
            
            verified, idx = verify_messages(ga_message.text.replace('\xa0', ' '), settlement_request)
            
            if verified :
                response.matching_message = ga_message
                response.matching_index = idx
                
                request_exists = await settlement_request_dao.get_report_by_groupa(ga_message.chat_id, ga_message.id, idx)
                # print(request_exists)
                if request_exists:
                    response.status = response_types.ALREADY_VERIFIED
                else:
                    user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.id) if ga_message.sender.id else False
                    if not user_whitelisted and ga_message.sender.username:
                        user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.username)
                        
                    if user_whitelisted:
                        response.status = response_types.VERIFIED
                        return response
                    else:
                        response.status = response_types.NOT_CONFIRMED
                        return response
                

        return response
    
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        response.status = ""
        return response
    
    


