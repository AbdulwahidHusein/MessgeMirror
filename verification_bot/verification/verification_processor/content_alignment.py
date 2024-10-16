
import re
from .models import SettlementRequest
from .parse_request import get_settlment_reqmodel
    


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

                match_count = 0
                if bank_account_number_idx != -1 and check_strict_ends_with(message_lines[bank_account_number_idx], request.bank_account_number):
                    match_count += 1
                if bank_account_name_idx != -1 and check_strict_ends_with(message_lines[bank_account_name_idx], request.bank_account_name):
                    match_count += 1
                if amount_idx != -1 and check_strict_ends_with(message_lines[amount_idx], request.amount):
                    match_count += 1
                if bank_name_idx != -1 and check_strict_ends_with(message_lines[bank_name_idx], request.bank_name):
                    match_count += 1
                if match_count == 4:
                    return (True, found_index)
                
    return (False, found_index)



    
    
if __name__ == "__main__":
    ga_message = """
        Amount :  THB 360000
                Bank :   SCB
                Bank account number    8602315265
                Bank account name :   Daka Runn
                
                Amount :  THB 360000
                Bank :   SCB
                Bank account number    8602315265
                Bank account name :   Daka d Run 
                
            Amount :  THB 360000
                Bank :   SCB
                Bank account number    8602315265
                Bank account nasme :   Dsaka Run 
                
                as
                Amount :  THB 360000
                Bank :   SCB
                Bank account number    8602315265
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

    model = get_settlment_reqmodel(gb_message)
    print(verify_messages(ga_message, model))
    
    