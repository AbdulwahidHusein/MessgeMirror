from pydantic import BaseModel
from datetime import datetime


class GroupPair(BaseModel):
    source_group_id : int
    target_group_id : int
    created_at : datetime
    
class SettlementRequestReport(BaseModel):
    groupa_id : int
    groupb_id : int
    created_at : datetime
    request_date : datetime
    sorce_group_message_id : int
    destination_group_message_id: int
    response : str