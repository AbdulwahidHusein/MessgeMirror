import re
from fuzzywuzzy import fuzz
from .models import SettlementRequest


def contains_settlement_request(text):
    lines = text.lower().splitlines()
    target_phrase = "settlement request:"

    for i, line in enumerate(lines[:2]):  # We only check the first two lines
        similarity = fuzz.partial_ratio(target_phrase, line)
        
        if similarity >= 80:
            return True
    return False



def get_bank_account_number_from_request(request_message: str) -> str:
    pattern1 = r"Bank\s*account\s*number\s*:?\s*([0-9\- ]+)"
    pattern2 = r"account\s*number\s*:?\s*([0-9\- ]+)"
    pattern3 = r"Bank-account-number\s*:?\s*([0-9\-]+)"
    pattern4 = r"account-number\s*:?\s*([0-9\-]+)"
    match = re.search(pattern1, request_message, re.IGNORECASE)
    
    if not match:
        match = re.search(pattern2, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern3, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern4, request_message, re.IGNORECASE)
        
    if match:
        return match.group(1)
    return ""



def get_bank_name_from_request(request_message: str) -> str:
    pattern1 = r"Bank\s*:?[\s]*(\w+)"
    pattern2 = r"bank\s*name\s*:?[\s]*(\w+)"
    match = re.search(pattern1, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern2, request_message, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return ""


def get_amount_from_request(request_message: str) -> str:
    pattern1 = r"Amount\s*:?[\s]*([^\n]+)"
    pattern2 = r"amt\s*:?[\s]*([^\n]+)"
    pattern3 = r"balance\s*:?[\s]*([^\n]+)"
    pattern4 = r"amount\s*balance\s*:?[\s]*([^\n]+)"
    
    match = re.search(pattern1, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern2, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern3, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern4, request_message, re.IGNORECASE)
    if match:
        return match.group(1).strip()  
    return ""


def get_bank_account_name_from_request(request_message: str) -> str:
    pattern1 = r"account\s*name\s*:?[\s]*([^\n]+)"
    
    pattern2 = r"bank\s*account\s*name\s*:?[\s]*([^\n]+)"
    pattern3 = r"account-name\s*:?[\s]*([^\n]+)"
    pattern4 = r"bank-account-name\s*:?[\s]*([^\n]+)"
    
    match = re.search(pattern1, request_message, re.IGNORECASE)
    
    if not match:
        match = re.search(pattern2, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern3, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern4, request_message, re.IGNORECASE)
    if match:
        return match.group(1).strip() 
    
    return ""

def get_merchant_name_from_request(request_message: str) -> str:
    pattern1 = r"merchant\s*name\s*:?[\s]*([^\n]+)"
    pattern2 = r"merchant-name\s*:?[\s]*([^\n]+)"
    match = re.search(pattern1, request_message, re.IGNORECASE)
    if not match:
        match = re.search(pattern2, request_message, re.IGNORECASE)
    if match:
        return match.group(1).strip()   
    return ""

def get_settlment_reqmodel(message: str) ->SettlementRequest:
    req = SettlementRequest()
    
    req.bank_account_name = get_bank_account_name_from_request(message)
    req.bank_account_number = get_bank_account_number_from_request(message)
    
    req.amount = get_amount_from_request(message)
    req.bank_name = get_bank_name_from_request(message)
    
    req.merchant_name = get_merchant_name_from_request(message)
    
    return req
    