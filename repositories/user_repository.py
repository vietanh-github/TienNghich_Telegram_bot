"""
User Repository
Handles database operations for users
"""
from typing import List, Optional
from database.connection import get_db
from database.models import User
from datetime import datetime
from pymongo import UpdateOne

class UserRepository:
    """Repository for user operations"""
    
    def __init__(self):
        self.collection = get_db().users
    
    def upsert_user(self, user: User) -> bool:
        """
        Insert or update a user
        Returns True if successful
        """
        try:
            data = user.to_dict()
            # Remove _id if it's None to allow MongoDB to generate it on insert
            if "_id" in data and data["_id"] is None:
                del data["_id"]
                
            self.collection.update_one(
                {"user_id": user.user_id},
                {"$set": data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error upserting user: {e}")
            return False
            
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        try:
            data = self.collection.find_one({"user_id": user_id})
            if data:
                return User.from_dict(data)
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
            
    def get_all_users(self) -> List[User]:
        """Get all users"""
        try:
            cursor = self.collection.find({})
            return [User.from_dict(user) for user in cursor]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
            
    def count(self) -> int:
        """Count total users"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
            
    def count_active_since(self, since_date: datetime) -> int:
        """Count users active since a specific date"""
        try:
            return self.collection.count_documents({
                "last_active_at": {"$gte": since_date}
            })
        except Exception as e:
            print(f"Error counting active users: {e}")
            return 0
            
    def add_exp(self, user_id: int, amount: int) -> bool:
        """
        Add EXP to a user
        Returns True if successful
        """
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"exp": amount}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding exp to user {user_id}: {e}")
            return False
    def set_admin(self, user_id: int, is_admin: bool) -> bool:
        """
        Set admin status for a user
        Returns True if successful
        """
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"is_admin": is_admin}}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"Error setting admin status for user {user_id}: {e}")
            return False
