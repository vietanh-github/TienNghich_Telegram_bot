"""
User Service
Business logic for user operations
"""
from typing import List, Optional
from repositories.user_repository import UserRepository
from database.models import User
from datetime import datetime

class UserService:
    """Service for user operations"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        
    def track_user(self, telegram_user) -> bool:
        """
        Track user interaction
        Update user info if exists, create if not
        """
        try:
            user = self.user_repo.get_by_id(telegram_user.id)
            
            if user:
                # Update existing user
                user.username = telegram_user.username or ""
                user.first_name = telegram_user.first_name or ""
                user.last_name = telegram_user.last_name or ""
                user.last_active_at = datetime.utcnow()
                user.updated_at = datetime.utcnow()
            else:
                # Create new user
                user = User(
                    user_id=telegram_user.id,
                    username=telegram_user.username or "",
                    first_name=telegram_user.first_name or "",
                    last_name=telegram_user.last_name or "",
                    last_active_at=datetime.utcnow()
                )
            
            return self.user_repo.upsert_user(user)
        except Exception as e:
            print(f"Error tracking user: {e}")
            return False
            
    def get_all_users(self) -> List[User]:
        """Get all users for broadcast"""
        return self.user_repo.get_all_users()
        
    def count_users(self) -> int:
        """Get total number of users"""
        return self.user_repo.count()

    def set_admin_status(self, user_id: int, is_admin: bool) -> bool:
        """Set admin status for a user"""
        return self.user_repo.set_admin(user_id, is_admin)
        
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin (including superuser)"""
        from config.settings import settings
        if user_id == settings.ADMIN_ID:
            return True
            
        user = self.user_repo.get_by_id(user_id)
        return user.is_admin if user else False
