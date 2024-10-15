
import re
from pydantic import BaseModel
from typing import Optional, Dict


from typing import Optional
from pydantic import BaseModel

class SettlementRequest(BaseModel):
    merchant_name: Optional[str] = None
    amount: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None


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

def get_settlment_reqmodel(message: str) ->SettlementRequest:
    req = SettlementRequest()
    
    req.bank_account_name = get_bank_account_name_from_request(message)
    req.bank_account_number = get_bank_account_number_from_request(message)
    
    req.amount = get_amount_from_request(message)
    req.bank_name = get_bank_name_from_request(message)
    
    return req
    

    

# Example usage:

def check_strict_ends_with(string_a, string_b):
    """
    This function checks if string_a ends with string_b but ensures that before string_b starts,
    string_a has a space, colon, or other delimiter, not a letter or number.
    """
    
    # print(string_a, string_b)
    
    string_a = string_a.strip()  # Trim leading/trailing spaces from string_a
    string_b = string_b.strip()  # Trim leading/trailing spaces from string_b

    # If string_a is shorter than string_b, return False
    if len(string_a) < len(string_b):
        # print(ga_message, gb_message)
        return False

    # Check if the end of string_a matches string_b
    if string_a[-len(string_b):] != string_b:
        # print(ga_message, gb_message)
        return False
    
    # Check the character just before string_b starts in string_a
    if len(string_a) == len(string_b):  # string_b is the whole string_a
        return True  # Perfect match

    # If there's a character before string_b in string_a, check if it's a space, colon, or delimiter
    preceding_char = string_a[-len(string_b) - 1]
    if preceding_char in (' ', ':', ",", "."):
        return True
    
    # If the preceding character is not a valid delimiter, it's a false match
    # print(ga_message, gb_message)
    return False

    


def verify_messages(ga_message, request : SettlementRequest):
    
    
    #ignore comma in amount
    ga_message = re.sub(r'(?<=\d)[,-](?=\d)', '', ga_message)

    request.amount = request.amount.replace(',','')
    request.bank_account_number = request.bank_account_number.replace('-','')
    
    
    message_lines = [line.strip() for line in ga_message.split("\n") if line.strip()]
    # print(message_lines)
    bank_account_name_poses = []
    bank_account_number_poses = []
    amount_poses = []
    bank_name_poses = []
    
    # Find positions of matches in the message
    for i, current_line in enumerate(message_lines):
        if request.bank_account_number in current_line:
            bank_account_number_poses.append((i, 0))
        if request.bank_account_name in current_line:
            bank_account_name_poses.append((i, 1))
        if request.amount in current_line:
            amount_poses.append((i, 2))
        if request.bank_name in current_line:
            bank_name_poses.append((i, 3))
    
    # Combine all positions
    position_array = bank_account_name_poses + bank_account_number_poses + amount_poses + bank_name_poses
    
    # Sort by the first element (line index)
    position_array.sort()

    found_index = -1
    # Find a sequence of 4 consecutive line indexes with unique position identifiers (0, 1, 2, 3)
    for i in range(len(position_array) - 3):
        # Get the 4 positions starting at index i
        window = position_array[i:i+4]
        
        # Check if their line indexes are consecutive
        line_indexes = [pos[0] for pos in window]
        if line_indexes == list(range(line_indexes[0], line_indexes[0] + 4)):
            # Check if the second elements (0, 1, 2, 3) are all different and cover 0 to 3
            position_indexes = set(pos[1] for pos in window)
            if position_indexes == {0, 1, 2, 3}:
                found_index = line_indexes[0]
                break
                
    
    if found_index != -1:
        bank_account_number_idx = -1
        bank_account_name_idx = -1
        amount_idx = -1
        bank_name_idx = -1
        
        for j in range(i, i+4):
            if position_array[j][1] == 0:
                bank_account_number_idx = position_array[j][0]
            if position_array[j][1] == 1:
                bank_account_name_idx = position_array[j][0]
            if position_array[j][1] == 2:
                amount_idx = position_array[j][0]
            if position_array[j][1] == 3:
                bank_name_idx = position_array[j][0]

        
        if not check_strict_ends_with(message_lines[bank_account_number_idx], request.bank_account_number):
            return (False, found_index)
        if not check_strict_ends_with(message_lines[bank_account_name_idx], request.bank_account_name):
            return (False, found_index)
        if not check_strict_ends_with(message_lines[amount_idx], request.amount):
            return( False, found_index)
        if not check_strict_ends_with(message_lines[bank_name_idx], request.bank_name):
            return (False, found_index)
        return (True, found_index)
    return (False, found_index)


class ContentAlignmentVerification:
    def __init__(self, ga_message: str, gb_message: str):
        self.ga_message = ga_message
        self.gb_message = gb_message
        self.request_model = get_settlment_reqmodel(self.gb_message)

    def verify(self) -> bool:
        return verify_messages(self.ga_message, self.request_model)
    
    
    
if __name__ == "__main__":
    ga_message = """
            
            structue these settlment requests
            
            1. Merchant name 

            Amount :  THB100,000
            Bank :   BBL
            Bank account name :   บุญทึง บุญลา  
            Bank account number :   5140695908


            2. Merchant name 

            Amount :  THB100,000
            Bank :   BBL
            Bank account name :   นราวดี ปิ่นทองอนัน
            Bank account number :   8800225958


            3. Merchant name 

            Amount :  THB1000000
            Bank :   BBL
            Bank account name :   จุฑามาศ ชาญอาวุธ
            Bank account number :  0784186827


            4. Merchant name 

            Amount :  THB100,000
            Bank :   BBLT
            Bank account name :  ชนาพร ดวงดารา
            Bank account number :  7357316889


            5. Merchant name 

            Amount :  THB100,0000
            Bank :   BBL
            Bank account name :  มลฤดี จันทรง 
            Bank account number :  6730473367
            
            Amount :  THB 360,000
            Bank :   SCB
            Bank account number    860-231526-5
            Bank account name :   Daka Run
            
            """
            
    gb_message = """
    Settlement Request

    W69

    Amount :  THB 360000
    Bank :   SCB
    Bank account number    8602315265
    Bank account name :   Daka Run
    """

    verifier = ContentAlignmentVerification(ga_message, gb_message)
    print(verifier.verify())
    
    