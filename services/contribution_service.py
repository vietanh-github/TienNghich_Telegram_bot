"""
Contribution service
Business logic for handling user contributions
"""
from typing import Optional, Tuple
from repositories import (
    ContributionRepository,
    MappingRepository,
    NovelRepository,
    EpisodeRepository
)
from database.models import Contribution, Mapping, Link
from utils.constants import *
from datetime import datetime


class ContributionService:
    """Service for contribution operations"""
    
    def __init__(self):
        self.contribution_repo = ContributionRepository()
        self.mapping_repo = MappingRepository()
        self.novel_repo = NovelRepository()
        self.episode_3d_repo = EpisodeRepository("3d")
        self.episode_2d_repo = EpisodeRepository("2d")
    
    def submit_mapping_contribution(
        self,
        user_id: int,
        username: str,
        novel_chapters: list,
        episode_3d: Optional[int] = None,
        episode_2d: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Contribution]]:
        """
        Submit a mapping contribution
        
        Returns:
            (success, message, contribution)
        """
        try:
            # Validate that at least one episode is specified
            if not episode_3d and not episode_2d:
                return False, "Phải có ít nhất một tập phim (3D hoặc 2D)", None
            
            # Create contribution
            contribution = Contribution(
                user_id=user_id,
                username=username,
                contribution_type=CONTRIBUTION_TYPE_MAPPING,
                data={
                    "novel_chapters": novel_chapters,
                    "episode_3d": episode_3d,
                    "episode_2d": episode_2d
                }
            )
            
            # Save to database
            result = self.contribution_repo.create(contribution)
            
            if result:
                return True, "Đóng góp của bạn đã được gửi và đang chờ admin duyệt!", result
            else:
                return False, "Lỗi khi lưu đóng góp. Vui lòng thử lại sau.", None
                
        except Exception as e:
            print(f"Error submitting mapping contribution: {e}")
            return False, f"Lỗi hệ thống: {str(e)}", None
    
    def submit_link_contribution(
        self,
        user_id: int,
        username: str,
        target_type: str,
        target_number: int,
        source_name: str,
        url: str
    ) -> Tuple[bool, str, Optional[Contribution]]:
        """
        Submit a link contribution
        
        Returns:
            (success, message, contribution)
        """
        try:
            # Determine contribution type
            if target_type == TARGET_TYPE_NOVEL:
                contribution_type = CONTRIBUTION_TYPE_NOVEL_LINK
            elif target_type == TARGET_TYPE_EPISODE_3D:
                contribution_type = CONTRIBUTION_TYPE_EPISODE_3D_LINK
            elif target_type == TARGET_TYPE_EPISODE_2D:
                contribution_type = CONTRIBUTION_TYPE_EPISODE_2D_LINK
            else:
                return False, "Loại đóng góp không hợp lệ", None
            
            # Create contribution
            contribution = Contribution(
                user_id=user_id,
                username=username,
                contribution_type=contribution_type,
                data={
                    "target_type": target_type,
                    "target_number": target_number,
                    "link": {
                        "source_name": source_name,
                        "url": url
                    }
                }
            )
            
            # Save to database
            result = self.contribution_repo.create(contribution)
            
            if result:
                return True, "Đóng góp link của bạn đã được gửi và đang chờ admin duyệt!", result
            else:
                return False, "Lỗi khi lưu đóng góp. Vui lòng thử lại sau.", None
                
        except Exception as e:
            print(f"Error submitting link contribution: {e}")
            return False, f"Lỗi hệ thống: {str(e)}", None
    
    def get_pending_contributions(self):
        """Get all pending contributions"""
        try:
            return self.contribution_repo.find_pending()
        except Exception as e:
            print(f"Error getting pending contributions: {e}")
            return []
    
    def get_contribution_by_id(self, contribution_id: str):
        """Get contribution by ID"""
        try:
            return self.contribution_repo.find_by_id(contribution_id)
        except Exception as e:
            print(f"Error getting contribution: {e}")
            return None
    
    def approve_contribution(
        self,
        contribution_id: str,
        admin_id: int
    ) -> Tuple[bool, str]:
        """
        Approve a contribution and apply it to the main database
        
        Returns:
            (success, message)
        """
        try:
            # Get the contribution
            contribution = self.contribution_repo.find_by_id(contribution_id)
            
            if not contribution:
                return False, "Không tìm thấy đóng góp"
            
            if contribution.status != STATUS_PENDING:
                return False, f"Đóng góp này đã được xử lý ({contribution.status})"
            
            # Apply the contribution based on type
            success = False
            
            if contribution.contribution_type == CONTRIBUTION_TYPE_MAPPING:
                success = self._apply_mapping_contribution(contribution)
            
            elif contribution.contribution_type == CONTRIBUTION_TYPE_NOVEL_LINK:
                success = self._apply_novel_link_contribution(contribution)
            
            elif contribution.contribution_type == CONTRIBUTION_TYPE_EPISODE_3D_LINK:
                success = self._apply_episode_link_contribution(contribution, "3d")
            
            elif contribution.contribution_type == CONTRIBUTION_TYPE_EPISODE_2D_LINK:
                success = self._apply_episode_link_contribution(contribution, "2d")
            
            if success:
                # Mark as approved
                self.contribution_repo.approve(contribution_id, admin_id)
                
                # Award EXP to user
                try:
                    from repositories.user_repository import UserRepository
                    user_repo = UserRepository()
                    user_repo.add_exp(contribution.user_id, 1)
                    print(f"Awarded 1 EXP to user {contribution.user_id}")
                except Exception as e:
                    print(f"Error awarding EXP: {e}")
                    
                return True, "Đóng góp đã được duyệt, áp dụng thành công và cộng 1 EXP!"
            else:
                return False, "Lỗi khi áp dụng đóng góp"
                
        except Exception as e:
            print(f"Error approving contribution: {e}")
            return False, f"Lỗi hệ thống: {str(e)}"
    
    def reject_contribution(
        self,
        contribution_id: str,
        admin_id: int,
        note: str = ""
    ) -> Tuple[bool, str]:
        """
        Reject a contribution
        
        Returns:
            (success, message)
        """
        try:
            contribution = self.contribution_repo.find_by_id(contribution_id)
            
            if not contribution:
                return False, "Không tìm thấy đóng góp"
            
            if contribution.status != STATUS_PENDING:
                return False, f"Đóng góp này đã được xử lý ({contribution.status})"
            
            # Mark as rejected
            self.contribution_repo.reject(contribution_id, admin_id, note)
            return True, "Đóng góp đã bị từ chối"
            
        except Exception as e:
            print(f"Error rejecting contribution: {e}")
            return False, f"Lỗi hệ thống: {str(e)}"
    
    def _apply_mapping_contribution(self, contribution: Contribution) -> bool:
        """Apply a mapping contribution to the database"""
        try:
            data = contribution.data
            
            mapping = Mapping(
                novel_chapters=data.get("novel_chapters", []),
                episode_3d=data.get("episode_3d"),
                episode_2d=data.get("episode_2d")
            )
            
            result = self.mapping_repo.create(mapping)
            return result is not None
            
        except Exception as e:
            print(f"Error applying mapping contribution: {e}")
            return False
    
    def _apply_novel_link_contribution(self, contribution: Contribution) -> bool:
        """Apply a novel link contribution to the database"""
        try:
            data = contribution.data
            target_number = data.get("target_number")
            link_data = data.get("link", {})
            
            link = Link(
                source_name=link_data.get("source_name", ""),
                url=link_data.get("url", "")
            )
            
            return self.novel_repo.add_link(target_number, link)
            
        except Exception as e:
            print(f"Error applying novel link contribution: {e}")
            return False
    
    def _apply_episode_link_contribution(
        self,
        contribution: Contribution,
        episode_type: str
    ) -> bool:
        """Apply an episode link contribution to the database"""
        try:
            data = contribution.data
            target_number = data.get("target_number")
            link_data = data.get("link", {})
            
            link = Link(
                source_name=link_data.get("source_name", ""),
                url=link_data.get("url", "")
            )
            
            if episode_type == "3d":
                repo = self.episode_3d_repo
            else:
                repo = self.episode_2d_repo
            
            return repo.add_link(target_number, link)
            
        except Exception as e:
            print(f"Error applying episode link contribution: {e}")
            return False
