import re

def extract_settlement_requests(text):
    requests_list = []
    current_request = {}
    
    # Updated regex to allow optional spaces before and after the colon
    amount_pattern = re.compile(r"^Amount\s*:?\s*(\d+\s*\w+)")
    bank_pattern = re.compile(r"^Bank\s*:?\s*(\w+)")
    account_name_pattern = re.compile(r"^Bank account name\s*:?\s*(\d+\s*\w+)")
    account_number_pattern = re.compile(r"^Bank account number\s*:?\s*(\d+\s*\w+)")
    
    for line in text.splitlines():
        line = line.strip()  # Clean up spaces and newlines
        
        # Debugging: print the line to see what is being processed
        print(f"Processing line: {line}")
        
        # Try matching the line with the updated regex patterns
        amount_match = amount_pattern.match(line)
        bank_match = bank_pattern.match(line)
        account_name_match = account_name_pattern.match(line)
        account_number_match = account_number_pattern.match(line)
        
        if amount_match:
            current_request['Amount'] = amount_match.group(1).strip()
            print(f"Matched Amount: {current_request['Amount']}")
        elif bank_match:
            current_request['Bank'] = bank_match.group(1).strip()
            print(f"Matched Bank: {current_request['Bank']}")
        elif account_name_match:
            current_request['Bank account name'] = account_name_match.group(1).strip()
            print(f"Matched Bank account name: {current_request['Bank account name']}")
        elif account_number_match:
            current_request['Bank account number'] = account_number_match.group(1).strip()
            print(f"Matched Bank account number: {current_request['Bank account number']}")

        # If all fields are found, append the current request and reset for the next one
        if len(current_request) == 4:
            requests_list.append(current_request)
            print(f"Completed request: {current_request}")
            current_request = {}

    return requests_list

# Sample text input
text = """
Settlement Request
Merchant name: m98
Amount    150.000
Bank  KBANK
Bank account name  นางสาว บุตษยา พันธ์บุตร
Bank account number 0528411061

Settlement Request
Merchant name: m98
Amount:150.000
Bank:KBANK
Bank account name: นางสาว บุตษยา พันธ์บุตร
Bank account number: 0528411061

Settlement Request
Merchant name: m98
Amount 100.000
Bank : BBL
Bank account name  :   รินรดา แซ่ลี้
Bank account number 2625362229
"""

# Call the function and print the result
requests = extract_settlement_requests(text)
print("Final Requests:", requests)
