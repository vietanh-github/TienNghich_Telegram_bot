"""
Mapping repository
Handles database operations for mappings between novels and episodes
"""
from typing import Optional, List
from database.connection import get_db
from database.models import Mapping
from datetime import datetime


class MappingRepository:
    """Repository for mappings"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.mappings
    
    def find_by_chapter(self, chapter_number: int) -> List[Mapping]:
        """Find all mappings that include a specific chapter"""
        try:
            cursor = self.collection.find(
                {"novel_chapters": chapter_number}
            )
            return [Mapping.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding mappings by chapter: {e}")
            return []
    
    def find_by_episode_3d(self, episode_number: int) -> Optional[Mapping]:
        """Find mapping by 3D episode number"""
        try:
            data = self.collection.find_one({"episode_3d": episode_number})
            if data:
                return Mapping.from_dict(data)
            return None
        except Exception as e:
            print(f"Error finding mapping by 3D episode: {e}")
            return None
    
    def find_by_episode_2d(self, episode_number: int) -> Optional[Mapping]:
        """Find mapping by 2D episode number"""
        try:
            data = self.collection.find_one({"episode_2d": episode_number})
            if data:
                return Mapping.from_dict(data)
            return None
        except Exception as e:
            print(f"Error finding mapping by 2D episode: {e}")
            return None
    
    def create(self, mapping: Mapping) -> Optional[Mapping]:
        """Create a new mapping"""
        try:
            # Validate that at least one episode is specified
            if not mapping.episode_3d and not mapping.episode_2d:
                print("Mapping must have at least one episode (3D or 2D)")
                return None
            
            # Check for existing mapping to update
            existing = None
            if mapping.episode_3d:
                existing = self.find_by_episode_3d(mapping.episode_3d)
            
            if not existing and mapping.episode_2d:
                existing = self.find_by_episode_2d(mapping.episode_2d)
                
            if existing:
                print(f"Updating existing mapping {existing._id}")
                # Update fields
                existing.novel_chapters = mapping.novel_chapters
                if mapping.episode_3d: existing.episode_3d = mapping.episode_3d
                if mapping.episode_2d: existing.episode_2d = mapping.episode_2d
                existing.updated_at = datetime.utcnow()
                
                self.update(existing._id, existing)
                return existing
            
            result = self.collection.insert_one(mapping.to_dict())
            mapping._id = result.inserted_id
            return mapping
        except Exception as e:
            print(f"Error creating/updating mapping: {e}")
            return None
    
    def update(self, mapping_id, mapping: Mapping) -> bool:
        """Update an existing mapping"""
        try:
            mapping.updated_at = datetime.utcnow()
            result = self.collection.update_one(
                {"_id": mapping_id},
                {"$set": mapping.to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating mapping: {e}")
            return False
    
    def delete(self, mapping_id) -> bool:
        """Delete a mapping"""
        try:
            result = self.collection.delete_one({"_id": mapping_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting mapping: {e}")
            return False
    
    def find_all(self) -> List[Mapping]:
        """Find all mappings"""
        try:
            cursor = self.collection.find()
            return [Mapping.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding all mappings: {e}")
            return []
            
    def get_all_mappings_sorted(self, limit: int = 20, offset: int = 0) -> List[Mapping]:
        """Get all mappings sorted by 3D episode desc"""
        try:
            # Sort by episode_3d desc, treating nulls as last (or filtered out if desired, but we want all)
            # Actually, let's just sort by _id desc as a proxy for recency, 
            # OR sort by episode_3d using a custom collation if needed. 
            # Simple sort: episode_3d -1. 
            cursor = self.collection.find()\
                .sort([("episode_3d", -1), ("episode_2d", -1)])\
                .skip(offset)\
                .limit(limit)
            return [Mapping.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error getting sorted mappings: {e}")
            return []
    
    def count(self) -> int:
        """Count total mappings"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting mappings: {e}")
            return 0
