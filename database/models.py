"""
Data models and schemas
Defines the structure of data objects
"""
from datetime import datetime
from typing import List, Optional, Dict, Any


class Link:
    """Link model for storing URLs with source names"""
    
    def __init__(self, source_name: str, url: str):
        self.source_name = source_name
        self.url = url
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "source_name": self.source_name,
            "url": self.url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Link':
        return cls(
            source_name=data.get("source_name", ""),
            url=data.get("url", "")
        )


class Novel:
    """Novel chapter model"""
    
    def __init__(
        self,
        chapter_number: int,
        title: str = "",
        links: Optional[List[Link]] = None,
        _id: Optional[Any] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.chapter_number = chapter_number
        self.title = title
        self.links = links or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "chapter_number": self.chapter_number,
            "title": self.title,
            "links": [link.to_dict() for link in self.links],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Novel':
        return cls(
            _id=data.get("_id"),
            chapter_number=data.get("chapter_number"),
            title=data.get("title", ""),
            links=[Link.from_dict(link) for link in data.get("links", [])],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class Episode:
    """Episode model (for both 3D and 2D)"""
    
    def __init__(
        self,
        episode_number: int,
        title: str = "",
        links: Optional[List[Link]] = None,
        _id: Optional[Any] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.episode_number = episode_number
        self.title = title
        self.links = links or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "episode_number": self.episode_number,
            "title": self.title,
            "links": [link.to_dict() for link in self.links],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        return cls(
            _id=data.get("_id"),
            episode_number=data.get("episode_number"),
            title=data.get("title", ""),
            links=[Link.from_dict(link) for link in data.get("links", [])],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class Mapping:
    """Mapping between novel chapters and episodes"""
    
    def __init__(
        self,
        novel_chapters: List[int],
        episode_3d: Optional[int] = None,
        episode_2d: Optional[int] = None,
        _id: Optional[Any] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.novel_chapters = novel_chapters
        self.episode_3d = episode_3d
        self.episode_2d = episode_2d
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "novel_chapters": self.novel_chapters,
            "episode_3d": self.episode_3d,
            "episode_2d": self.episode_2d,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mapping':
        return cls(
            _id=data.get("_id"),
            novel_chapters=data.get("novel_chapters", []),
            episode_3d=data.get("episode_3d"),
            episode_2d=data.get("episode_2d"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class Contribution:
    """User contribution model"""
    
    def __init__(
        self,
        user_id: int,
        username: str,
        contribution_type: str,
        data: Dict[str, Any],
        status: str = "pending",
        admin_note: str = "",
        _id: Optional[Any] = None,
        submitted_at: Optional[datetime] = None,
        reviewed_at: Optional[datetime] = None,
        reviewed_by: Optional[int] = None
    ):
        self._id = _id
        self.user_id = user_id
        self.username = username
        self.contribution_type = contribution_type
        self.data = data
        self.status = status
        self.admin_note = admin_note
        self.submitted_at = submitted_at or datetime.utcnow()
        self.reviewed_at = reviewed_at
        self.reviewed_by = reviewed_by
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "username": self.username,
            "contribution_type": self.contribution_type,
            "data": self.data,
            "status": self.status,
            "admin_note": self.admin_note,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contribution':
        return cls(
            _id=data.get("_id"),
            user_id=data.get("user_id"),
            username=data.get("username", ""),
            contribution_type=data.get("contribution_type"),
            data=data.get("data", {}),
            status=data.get("status", "pending"),
            admin_note=data.get("admin_note", ""),
            submitted_at=data.get("submitted_at"),
            reviewed_at=data.get("reviewed_at"),
            reviewed_by=data.get("reviewed_by")
        )


class User:
    """User model"""
    
    def __init__(
        self,
        user_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
        is_admin: bool = False,
        exp: int = 0,
        _id: Optional[Any] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_active_at: Optional[datetime] = None
    ):
        self._id = _id
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        self.exp = exp
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_active_at = last_active_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_admin": self.is_admin,
            "exp": self.exp,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_active_at": self.last_active_at
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            _id=data.get("_id"),
            user_id=data.get("user_id"),
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            is_admin=data.get("is_admin", False),
            exp=data.get("exp", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            last_active_at=data.get("last_active_at")
        )

