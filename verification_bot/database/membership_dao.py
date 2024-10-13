# membership_manager.py

from .db import membership_collection
from typing import List, Dict, Optional

def create_member_ship(group_info: Dict) -> Optional[str]:
    """Add or update a membership group entry in the database."""
    group_id = group_info['id']
    result = membership_collection.update_one(
        {'id': group_id},
        {'$set': {"group_id": group_id, 'group_data': group_info}},
        upsert=True
    )
    return str(result.upserted_id) if result.upserted_id else None

def delete_member_ship(group_id: int) -> int:
    """Delete a membership group by its group_id."""
    result = membership_collection.delete_one({'group_id': group_id})
    return result.deleted_count

def get_member_ship_groups() -> List[Dict]:
    """Retrieve all membership groups."""
    return list(membership_collection.find())

def get_member_shipgroup_by_id(group_id: int) -> Optional[Dict]:
    """Retrieve a membership group by its group_id."""
    return membership_collection.find_one({'group_id': group_id})
