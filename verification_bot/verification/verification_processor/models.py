from pydantic import BaseModel
from typing import Optional, Dict, List, Any


from typing import Optional
from pydantic import BaseModel

class SettlementRequest(BaseModel):
    merchant_name: Optional[str] = None
    amount: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    
    
class HandleResponse(BaseModel):
    status: Optional[str] = None
    similar_messages: Optional[List[Any]] = None  
    matching_message: Optional[Any] = None 
    matching_index: Optional[int] = None