
from pydantic import BaseModel
import os
from typing import List, Optional
from groq import Groq
import instructor

class SettlementRequest(BaseModel):
    merchant_name: Optional[str] = None
    amount: Optional[str] = None
    bank: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    
class SettlementBatch(BaseModel):
    requests: List[SettlementRequest]


model = "llama3-groq-70b-8192-tool-use-preview"


client = Groq(
    api_key='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',
)

client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)


resp = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": """
            
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

            Amount :  THB100,000
            Bank :   BBL
            Bank account name :   จุฑามาศ ชาญอาวุธ
            Bank account number :  0784186827


            4. Merchant name 

            Amount :  THB100,000
            Bank :   BBL
            Bank account name :  ชนาพร ดวงดารา
            Bank account number :  7357316889


            5. Merchant name 

            Amount :  THB100,000
            Bank :   BBL
            Bank account name :  มลฤดี จันทรง 
            Bank account number :  6730473367
            
            
            """,
        }
    ],
    response_model=SettlementBatch,
)

print(resp.model_dump_json(indent=2))