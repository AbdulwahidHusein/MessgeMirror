import logging
from . import telegram_client
from .content_alignment import verify_messages
from .parse_request import get_settlement_request_model
from .models import HandleResponse
from verification_bot.database import whitelist_dao, settlement_request_dao
from . import response_types as response_types
from typing import Any
from collections import defaultdict

async def handle(message: dict, source_group_id: Any, source_group_title: str) -> HandleResponse:
    response = HandleResponse(status=response_types.NOT_VERIFIED)
    
    try:
        settlement_request = get_settlement_request_model(message['text'])


        if settlement_request and settlement_request.merchant_name.lower() not in source_group_title.lower():
            response.status = response_types.NOT_CONFIRMED
            return response
        
        similar_messages = await telegram_client.search_messages(source_group_id, settlement_request)
        
        matching_messages = defaultdict(list)
        non_matching_messages = []
        
        for ga_message in similar_messages:
            matches, idx = verify_messages(ga_message.text.replace('\xa0', ''), settlement_request)
            if matches:
                already_exists = await settlement_request_dao.get_report_by_groupa(ga_message.chat_id, ga_message.id, idx)
                if already_exists:
                    matching_messages['already_verified'].append(ga_message)
                    continue
                
                user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.id) if ga_message.sender.id else False
                if not user_whitelisted and ga_message.sender.username:
                    user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.username)
                
                if not user_whitelisted:
                    matching_messages['user_not_whitelisted'].append(ga_message)
                    continue
                
                if user_whitelisted and not already_exists:
                    matching_messages['verified'].append((ga_message, idx))
            else:
                non_matching_messages.append(ga_message)
                
        if matching_messages['verified']:
            response.status = response_types.VERIFIED
            response.matching_index = matching_messages['verified'][0][1]
            response.matching_message = matching_messages['verified'][0][0]
            return response

        if matching_messages['user_not_whitelisted']:
            response.status = response_types.NOT_CONFIRMED
            response.similar_messages = matching_messages['user_not_whitelisted']
            return response
        
        if matching_messages['already_verified']:
            response.status = response_types.ALREADY_VERIFIED
            response.similar_messages = matching_messages['already_verified']
            return response
        
    
        response.status = response_types.NOT_VERIFIED
        return response
        

        # response.similar_messages = similar_messages

        # for ga_message in similar_messages:
            
            
        #     verified, idx = verify_messages(ga_message.text.replace('\xa0', ''), settlement_request)
            
        #     if verified :
        #         response.matching_message = ga_message
        #         response.matching_index = idx
                
        #         request_exists = await settlement_request_dao.get_report_by_groupa(ga_message.chat_id, ga_message.id, idx)
        #         # print(request_exists)
        #         if request_exists:
        #             response.status = response_types.ALREADY_VERIFIED
        #         else:
        #             user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.id) if ga_message.sender.id else False
        #             if not user_whitelisted and ga_message.sender.username:
        #                 user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.username)
                        
        #             if user_whitelisted:
        #                 response.status = response_types.VERIFIED
        #                 return response
        #             else:
        #                 response.status = response_types.NOT_CONFIRMED
                

        return response
    
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        response.status = ""
        return response
    
    


