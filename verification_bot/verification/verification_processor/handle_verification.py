import logging
from . import telegram_client
from .content_alignment import verify_messages
from .parse_request import get_settlment_reqmodel
from .models import HandleResponse
from verification_bot.database import whitelist_dao, settlement_request_dao

async def handle(message: dict, source_group_id: int, source_group_title: str) -> HandleResponse:
    response = HandleResponse(status='Not Verified')
    
    try:
        settlement_request = get_settlment_reqmodel(message['text'])
        

        if settlement_request and settlement_request.merchant_name not in source_group_title:
            response.status = "merchant name not in group"
            return response
        
        similar_messages = await telegram_client.search_messages(source_group_id, settlement_request.bank_account_number)

        response.similar_messages = similar_messages

        for ga_message in similar_messages:
            
            
            verified, idx = verify_messages(ga_message.text, settlement_request)
            
            if verified :
                response.matching_message = ga_message
                response.matching_index = idx
                
                message_exists = settlement_request_dao.get_report_by_groupa(ga_message.chat_id, ga_message.id, idx)
                # print(message_exists)
                if message_exists:
                    response.status = "already verified"
                else:
                    user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.id) if ga_message.sender.id else False
                    if not user_whitelisted and ga_message.sender.username:
                        user_whitelisted = whitelist_dao.is_whitelisted(ga_message.sender.username)
                
                    if user_whitelisted:
                        response.status = 'verified'
                        return response
                    else:
                        response.status = 'sender not confirmed'
                

        if not response.matching_message:
            response.status = 'Not verified'
        
        return response
    
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        response.status = ""
        return response
