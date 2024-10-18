from datetime import datetime, timezone
from .db import settlement_requests_collection
from bson import ObjectId
from typing import List, Optional

def convert_object_id(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# Create a new SettlementRequestReport
async def create_settlement_request_report(groupa_id: int, groupb_id: int, groupa_message_id: int = None, groupb_message_id: int = None, status: str = None, index_on_groupa: int = None, groupa_similar_message_ids: List[int] = None) -> str:
    new_report = {
        "groupa_id": groupa_id,
        "groupb_id": groupb_id,
        "created_at": datetime.now(timezone.utc),
        "request_date": datetime.now(timezone.utc),
        "groupa_message_id": groupa_message_id,
        "groupb_message_id": groupb_message_id,
        "status": status,
        "index_on_groupa": index_on_groupa,
        "groupa_similar_message_ids" : groupa_similar_message_ids,
    }
    result = settlement_requests_collection.insert_one(new_report)
    return str(result.inserted_id)

# Function to get report by groupa_id, groupa_message_id, and index_on_groupa
async def get_report_by_groupa(groupa_id: int, groupa_message_id: int = None, index_on_groupa: int = None):
    query = {
        "groupa_id": groupa_id,
    }
    if groupa_message_id is not None:
        query["groupa_message_id"] = groupa_message_id
    if index_on_groupa is not None:
        query["index_on_groupa"] = index_on_groupa
    
    reports = settlement_requests_collection.find(query)
    return list(reports)


async def get_report_by_groupb(groupb_id: int, groupb_message_id: int = None, status: str = None):
    query = {
        "groupb_id": groupb_id,
    }
    if groupb_message_id is not None:
        query["groupb_message_id"] = groupb_message_id
    if status is not None:
        query["status"] = status
    
    reports = settlement_requests_collection.find(query)
    return list(reports)



async def get_report(
        groupa_id: Optional[int] = None,
        groupb_id: Optional[int] = None,
        groupa_message_id: Optional[int] = None,
        groupb_message_id: Optional[int] = None,
        status: Optional[str] = None,
        index_on_groupa: Optional[int] = None,
        groupa_similar_message_ids: Optional[List[int]] = None,
        created_at: Optional[datetime] = None,
        request_date: Optional[datetime] = None
    ):
    
    query = {}
    
    if groupa_id is not None:
        query["groupa_id"] = groupa_id
    if groupb_id is not None:
        query["groupb_id"] = groupb_id
    if groupa_message_id is not None:
        query["groupa_message_id"] = groupa_message_id
    if groupb_message_id is not None:
        query["groupb_message_id"] = groupb_message_id
    if status is not None:
        query["status"] = status
    if index_on_groupa is not None:
        query["index_on_groupa"] = index_on_groupa
    if groupa_similar_message_ids is not None:
        query["groupa_similar_message_ids"] = groupa_similar_message_ids
    if created_at is not None:
        query["created_at"] = {"$gte": created_at}  # Filter by created_at if provided
    if request_date is not None:
        query["request_date"] = {"$gte": request_date}  # Filter by request_date if provided

    reports = settlement_requests_collection.find(query)
    
    return list(reports)