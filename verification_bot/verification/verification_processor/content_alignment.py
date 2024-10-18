
import re
from .models import SettlementRequest
from .parse_request import get_settlement_request_model, flexible_string_search
    


def check_strict_ends_with(string_a, string_b):
    """
    This function checks if string_a ends with string_b but ensures that before string_b starts,
    string_a has a space, colon, or other delimiter, not a letter or number.
    """
    
    # print(string_a, string_b)
    
    string_a = string_a.strip()
    string_b = string_b.strip()
    
    
    

    # If string_a is shorter than string_b, return False
    if len(string_a) < len(string_b):
        # print(ga_message, gb_message)
        return False
    
    enda = len(string_a) - 1
    endb = len(string_b) - 1
    
    specials = [' ', '-', "/", ","]
    
    while enda >= 0 and endb >= 0:
        if string_a[enda] in specials:
            enda -= 1
        else:
            if string_a[enda].lower() != string_b[endb].lower():
                return False
            enda -= 1
            endb -= 1
            
    if endb < 0 and  enda >=0 and string_a[enda] in (' ', ':', ",", "."):
        return True
    if enda == -1 and endb == -1:
        return True
    return False

    


def verify_messages(ga_message, request : SettlementRequest):
    
    message_lines = [line.strip() for line in ga_message.split("\n") if line.strip()]
    # print(message_lines)
    bank_account_name_poses = []
    bank_account_number_poses = []
    amount_poses = []
    bank_name_poses = []
    
    # Find positions of matches in the message
    for i, current_line in enumerate(message_lines):
        if flexible_string_search(current_line, request.bank_account_number):
            bank_account_number_poses.append((i, 0))
        if flexible_string_search(current_line, request.bank_account_name):
            bank_account_name_poses.append((i, 1))
        if flexible_string_search(current_line, request.amount):
            amount_poses.append((i, 2))
        if flexible_string_search(current_line, request.bank_name):
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
    comp = check_strict_ends_with("Amount :  THB 700,000", "THB700000")
    print(comp)
    
    