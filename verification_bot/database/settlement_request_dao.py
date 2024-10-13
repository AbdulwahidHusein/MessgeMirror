from datetime import datetime, timezone
from .db import settlement_requests_collection
from bson import ObjectId
from typing import List, Optional

def convert_object_id(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# Create a new SettlementRequestReport
def create_settlement_request_report(source_group_id: int, destination_group_id: int, source_group_message_id: int, destination_group_message_id: int, response: str) -> str:
    new_report = {
        "source_group_id": source_group_id,
        "destination_group_id": destination_group_id,
        "created_at": datetime.now(timezone.utc),
        "request_date": datetime.now(timezone.utc),
        "source_group_message_id": source_group_message_id,
        "destination_group_message_id": destination_group_message_id,
        "response": response
    }
    result = settlement_requests_collection.insert_one(new_report)
    return str(result.inserted_id)

# Read (Fetch) SettlementRequestReports by source_group_id
def get_settlement_requests_by_group_id(source_group_id: int) -> List[dict]:
    results = settlement_requests_collection.find({"source_group_id": source_group_id})
    return [convert_object_id(result) for result in results]

# Update a SettlementRequestReport by source_group_id and destination_group_message_id
def update_settlement_request_report(source_group_id: int, destination_group_message_id: int, response: Optional[str] = None) -> bool:
    update_data = {}
    if response is not None:
        update_data["response"] = response
    
    if update_data:
        result = settlement_requests_collection.update_one(
            {"source_group_id": source_group_id, "destination_group_message_id": destination_group_message_id},
            {"$set": update_data}
        )
        return result.modified_count > 0  # Return True if the update was successful
    return False

# Delete a SettlementRequestReport by source_group_id and destination_group_message_id
def delete_settlement_request_report(source_group_id: int, destination_group_message_id: int) -> bool:
    result = settlement_requests_collection.delete_one(
        {"source_group_id": source_group_id, "destination_group_message_id": destination_group_message_id}
    )
    return result.deleted_count > 0  # Return True if the deletion was successful
