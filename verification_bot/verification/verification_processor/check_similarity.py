from datetime import datetime
from typing import Optional
from fuzzywuzzy import fuzz



BASIC_SETTLEMENT_REQUEST_FIELDS = [
    "merchant name",
    "amount",
    "bank name",
    "bank account name",
    "bank account number"
]

SETTLEMENT_REQUEST_EXAMPLE = """
Settlement Request:
Merchant Name: ABC Store
Amount: USD 1000.00
Bank: Chase Bank
Bank Account Name: John Doe
"""

class SettlementRequest:
    def __init__(self, merchant_name: Optional[str] = None, amount: Optional[str] = None,
                 bank_name: Optional[str] = None, bank_account_name: Optional[str] = None,
                 bank_account_number: Optional[str] = None):
        self.merchant_name = merchant_name
        self.amount = amount
        self.bank_name = bank_name
        self.bank_account_name = bank_account_name
        self.bank_account_number = bank_account_number

def approximate_match(text: str, request: SettlementRequest, threshold: int = 80) -> bool:
    """
    Check if the given text approximately matches any of the fields in the SettlementRequest.

    Arguments:
    text -- the text to compare against the request fields.
    request -- the SettlementRequest object.
    threshold -- the similarity threshold (0-100).

    Returns:
    True if there's a match above the threshold, otherwise False.
    """
    # Prepare fields for comparison
    fields_to_check = [
        request.merchant_name,
        request.amount,
        request.bank_name,
        request.bank_account_name,
        request.bank_account_number
    ]
    matched_count = 0
    
    for field in fields_to_check:
        if field:  
            similarity = fuzz.partial_ratio(text.lower(), field.lower())
            if similarity >= threshold:
                matched_count += 1
                if matched_count >= 3:
                    return True  
    
    return False  # No matches found


def get_settlment_score(text):
    lower = text.lower()
    score = 0
    for field in BASIC_SETTLEMENT_REQUEST_FIELDS:
        similarity = fuzz.partial_ratio(lower, field.lower())
        score += similarity
        
    return score/ len(BASIC_SETTLEMENT_REQUEST_FIELDS)

if __name__ == "__main__":
    request = SettlementRequest(
        merchant_name="ABCStore",
        amount="100.00",
        bank_name="XYZBank",
        bank_account_name="fdgs df",
        bank_account_number="673-724-7715"
    )

    search_text = """
        Bank Account Number: 735-731-688-94
        Bank Account Name: ชนาพร
        Bank: bbLT
        Amount: THB 1,000,000

        Bank Account Number: 735-731-688-94
        Bank Account Name: ชนาพร ดวงดารา
        Bank: bbLT
        Amount: THB 1,000,000

        Bank Account Number: abc735731688-94
        Bank Account Name: ชนาพร ดวงดารา
        Bank: bbLT
        Amount: THB 1,000,000

        Bank Account Number: tbh 735731-688-94
        Bank Account Name: ชนาพร ดวงดารา
        Bank: bbLT
Amount: THB 1,000,000
    """  # Text to search for
    
    score = get_settlment_score(search_text)
    print(score)