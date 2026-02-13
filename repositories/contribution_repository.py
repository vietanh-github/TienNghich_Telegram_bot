"""
Contribution repository
Handles database operations for user contributions
"""
from typing import Optional, List
from bson import ObjectId
from database.connection import get_db
from database.models import Contribution
from datetime import datetime
from utils.constants import STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED


class ContributionRepository:
    """Repository for user contributions"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.contributions
    
    def create(self, contribution: Contribution) -> Optional[Contribution]:
        """Create a new contribution"""
        try:
            result = self.collection.insert_one(contribution.to_dict())
            contribution._id = result.inserted_id
            return contribution
        except Exception as e:
            print(f"Error creating contribution: {e}")
            return None
    
    def find_by_id(self, contribution_id: str) -> Optional[Contribution]:
        """Find contribution by ID"""
        try:
            data = self.collection.find_one({"_id": ObjectId(contribution_id)})
            if data:
                return Contribution.from_dict(data)
            return None
        except Exception as e:
            print(f"Error finding contribution: {e}")
            return None
    
    def find_pending(self) -> List[Contribution]:
        """Find all pending contributions"""
        try:
            cursor = self.collection.find(
                {"status": STATUS_PENDING}
            ).sort("submitted_at", -1)
            
            return [Contribution.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding pending contributions: {e}")
            return []
    
    def find_by_user(self, user_id: int) -> List[Contribution]:
        """Find all contributions by a user"""
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("submitted_at", -1)
            
            return [Contribution.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding user contributions: {e}")
            return []
    
    def find_by_status(self, status: str) -> List[Contribution]:
        """Find contributions by status"""
        try:
            cursor = self.collection.find(
                {"status": status}
            ).sort("submitted_at", -1)
            
            return [Contribution.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding contributions by status: {e}")
            return []
    
    def approve(self, contribution_id: str, admin_id: int, note: str = "") -> bool:
        """Approve a contribution"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(contribution_id)},
                {
                    "$set": {
                        "status": STATUS_APPROVED,
                        "reviewed_at": datetime.utcnow(),
                        "reviewed_by": admin_id,
                        "admin_note": note
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error approving contribution: {e}")
            return False
    
    def reject(self, contribution_id: str, admin_id: int, note: str = "") -> bool:
        """Reject a contribution"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(contribution_id)},
                {
                    "$set": {
                        "status": STATUS_REJECTED,
                        "reviewed_at": datetime.utcnow(),
                        "reviewed_by": admin_id,
                        "admin_note": note
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error rejecting contribution: {e}")
            return False
    
    def delete(self, contribution_id: str) -> bool:
        """Delete a contribution"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(contribution_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting contribution: {e}")
            return False
    
    def count_by_status(self, status: str) -> int:
        """Count contributions by status"""
        try:
            return self.collection.count_documents({"status": status})
        except Exception as e:
            print(f"Error counting contributions: {e}")
            return 0
    
    def count_pending(self) -> int:
        """Count pending contributions"""
        return self.count_by_status(STATUS_PENDING)
    
    def get_top_contributors(self, limit: int = 5) -> List[dict]:
        """
        Get top contributors based on approved contributions
        Returns list of dicts: {'_id': user_id, 'username': str, 'count': int}
        """
        try:
            pipeline = [
                {"$match": {"status": STATUS_APPROVED}},
                {"$group": {
                    "_id": "$user_id",
                    "username": {"$first": "$username"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error getting top contributors: {e}")
            return []
