"""
Admin service
Business logic for admin operations
"""
from repositories import (
    NovelRepository,
    EpisodeRepository,
    MappingRepository,
    ContributionRepository,
    UserRepository
)
from datetime import datetime, timedelta
from utils.constants import STATUS_PENDING


class AdminService:
    """Service for admin operations"""
    
    def __init__(self):
        self.novel_repo = NovelRepository()
        self.episode_3d_repo = EpisodeRepository("3d")
        self.episode_2d_repo = EpisodeRepository("2d")
        self.mapping_repo = MappingRepository()
        self.contribution_repo = ContributionRepository()
        self.user_repo = UserRepository()
    
    def get_statistics(self) -> dict:
        """Get database statistics"""
        try:
            now = datetime.utcnow()
            today_start = datetime(now.year, now.month, now.day)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            stats = {
                "total_novels": self.novel_repo.count(),
                "total_episodes_3d": self.episode_3d_repo.count(),
                "total_episodes_2d": self.episode_2d_repo.count(),
                "total_mappings": self.mapping_repo.count(),
                "pending_contributions": self.contribution_repo.count_pending(),
                
                # User stats
                "total_users": self.user_repo.count(),
                "active_today": self.user_repo.count_active_since(today_start),
                "active_week": self.user_repo.count_active_since(week_ago),
                "active_month": self.user_repo.count_active_since(month_ago),
                
                # Leaderboard
                "top_contributors": self.contribution_repo.get_top_contributors(5)
            }
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def get_pending_count(self) -> int:
        """Get count of pending contributions"""
        try:
            return self.contribution_repo.count_pending()
        except Exception as e:
            print(f"Error getting pending count: {e}")
            return 0
