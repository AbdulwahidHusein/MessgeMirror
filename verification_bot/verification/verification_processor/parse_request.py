import re
from fuzzywuzzy import fuzz
from .models import SettlementRequest

# Constant for target phrase to identify settlement requests
TARGET_PHRASE = "settlement request:"

def contains_settlement_request(text: str) -> bool:
    """Check if the text contains a settlement request."""
    lines = text.lower().splitlines()

    for line in lines[:2]:  # Check only the first two lines
        similarity = fuzz.partial_ratio(TARGET_PHRASE, line)
        if similarity >= 80:
            return True
            
    return False

def extract_data_with_patterns(request_message: str, patterns: list) -> str:
    """Extract data using a list of regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, request_message, re.IGNORECASE)
        if match:
            # Clean the extracted data by removing spaces, dashes, slashes, and commas
            return re.sub(r'[\s\-\/,]', '', match.group(1)).strip()
    
    return ""

def get_bank_account_number_from_request(request_message: str) -> str:
    """Extract the bank account number from the request message."""
    patterns = [
        r"Bank\s*account\s*number\s*:?\s*([0-9\- ]+)",
        r"account\s*number\s*:?\s*([0-9\- ]+)",
        r"Bank-account-number\s*:?\s*([0-9\-]+)",
        r"account-number\s*:?\s*([0-9\-]+)"
    ]
    return extract_data_with_patterns(request_message, patterns)

def get_bank_name_from_request(request_message: str) -> str:
    """Extract the bank name from the request message."""
    patterns = [
        r"bank\s*name\s*:?[\s]*([^\n]+)",
        r"Bank\s*:?[\s]*([^\n]+)",        
    ]
    return extract_data_with_patterns(request_message, patterns)

def get_amount_from_request(request_message: str) -> str: 
    """Extract the amount from the request message."""
    patterns = [
        r"amount\s*balance\s*:?[\s]*([^\n]+)",
        r"Amount\s*:?[\s]*([^\n]+)",
        r"amt\s*:?[\s]*([^\n]+)",
        r"balance\s*:?[\s]*([^\n]+)",
    ]
    return extract_data_with_patterns(request_message, patterns)

def get_bank_account_name_from_request(request_message: str) -> str:
    """Extract the bank account name from the request message."""
    patterns = [
        r"account\s*name\s*:?[\s]*([^\n]+)",
        r"bank\s*account\s*name\s*:?[\s]*([^\n]+)",
        r"account-name\s*:?[\s]*([^\n]+)",
        r"bank-account-name\s*:?[\s]*([^\n]+)"
    ]
    return extract_data_with_patterns(request_message, patterns)

def get_merchant_name_from_request(request_message: str) -> str:
    """Extract the merchant name from the request message."""
    patterns = [
        r"merchant\s*name\s*:?[\s]*([^\n]+)",
        r"merchant-name\s*:?[\s]*([^\n]+)",
        r"merchant\s*:?[\s]*([^\n]+)"
    ]
    return extract_data_with_patterns(request_message, patterns)

def get_settlement_request_model(message: str) -> SettlementRequest:
    print("message", message)
    """Construct a SettlementRequest model from the message."""
    req = SettlementRequest()
    
    req.bank_account_name = get_bank_account_name_from_request(message)
    req.bank_account_number = get_bank_account_number_from_request(message)
    req.amount = get_amount_from_request(message)
    req.bank_name = get_bank_name_from_request(message)
    req.merchant_name = get_merchant_name_from_request(message) 
    
    return req



def flexible_string_search(haystack: str, needle: str) -> bool:
    """
    Perform a flexible search where the 'needle' is compared to the 'haystack'
    after removing spaces, punctuation, and special characters, while keeping
    alphanumeric characters from any language.
    """
    # Remove non-letter, non-number characters (spaces, dashes, punctuation) from both strings
    # \w matches any Unicode word character (equivalent to [a-zA-Z0-9_] but also for other languages)
    clean_haystack = re.sub(r'[^\w]', '', haystack).lower()
    clean_needle = re.sub(r'[^\w]', '', needle).lower()
    
    # Check if the cleaned needle is a substring of the cleaned haystack
    return clean_needle in clean_haystack


if __name__ == "__main__":
    print(get_settlement_request_model("""
                                    settlment request
    merchant name M89

    Amount :  THB 700,000
    Bank name:   Bangkok Bank
    Bank account name :   MR ADITYA
    Bank account number :   542-7-12307-9"""))