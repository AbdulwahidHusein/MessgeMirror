from datetime import datetime, timezone
from .db import group_pairs_collection
from bson import ObjectId
from typing import List, Dict, Optional


# Create a new GroupPair
def create_group_pair(source_group_data: dict, dest_group_data: dict) -> str:
    new_group_pair = {
        "source_group_data": source_group_data,
        "dest_group_data": dest_group_data,
        "created_at": datetime.now(timezone.utc)
    }
    result = group_pairs_collection.insert_one(new_group_pair)
    return str(result.inserted_id)


def get_group_pairs() -> List[Dict]:
    results = group_pairs_collection.find()
    return [result for result in results]  

# Delete a GroupPair by source_group_id
def delete_group_pair(source_group_id: int) -> bool:
    # Assuming source_group_data.id is an integer; change as necessary
    result = group_pairs_collection.delete_one({"source_group_data.id": source_group_id})
    return result.deleted_count > 0


def has_group_pair(group_id: int) -> bool:
    result1 = group_pairs_collection.find_one({"source_group_data.id": group_id})
    result2 = group_pairs_collection.find_one({"dest_group_data.id": group_id})
    return result1 or result2

def get_source_group_data(dest_group_id: int) -> Optional[Dict]:
    result =  group_pairs_collection.find_one({"dest_group_data.id": dest_group_id})
    
    if result:
        return result['source_group_data']
    return None


def update_group_title(group_id: int, new_title: str) -> bool:
    # First, check if the group_id matches the source_group_data.id
    source_result = group_pairs_collection.update_one(
        {"source_group_data.id": group_id},
        {"$set": {"source_group_data.title": new_title}}
    )

    # If no source group was found, check for a destination group
    if source_result.modified_count == 0:
        dest_result = group_pairs_collection.update_one(
            {"dest_group_data.id": group_id},
            {"$set": {"dest_group_data.title": new_title}}
        )
        return dest_result.modified_count > 0

    return True  