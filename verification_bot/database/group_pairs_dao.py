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
