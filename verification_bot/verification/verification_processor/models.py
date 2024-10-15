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
