"""
Novel repository
Handles database operations for novel chapters
"""
from typing import Optional, List
from database.connection import get_db
from database.models import Novel, Link
from datetime import datetime


class NovelRepository:
    """Repository for novel chapters"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.novels
    
    def find_by_chapter_number(self, chapter_number: int) -> Optional[Novel]:
        """Find novel chapter by chapter number"""
        try:
            data = self.collection.find_one({"chapter_number": chapter_number})
            if data:
                return Novel.from_dict(data)
            return None
        except Exception as e:
            print(f"Error finding novel chapter: {e}")
            return None
    
    def find_by_chapter_numbers(self, chapter_numbers: List[int]) -> List[Novel]:
        """Find multiple novel chapters by chapter numbers"""
        try:
            cursor = self.collection.find(
                {"chapter_number": {"$in": chapter_numbers}}
            ).sort("chapter_number", 1)
            
            return [Novel.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding novel chapters: {e}")
            return []
    
    def create(self, novel: Novel) -> Optional[Novel]:
        """Create a new novel chapter"""
        try:
            # Check if chapter already exists
            existing = self.find_by_chapter_number(novel.chapter_number)
            if existing:
                print(f"Chapter {novel.chapter_number} already exists")
                return existing
            
            result = self.collection.insert_one(novel.to_dict())
            novel._id = result.inserted_id
            return novel
        except Exception as e:
            print(f"Error creating novel chapter: {e}")
            return None
    
    def update(self, novel: Novel) -> bool:
        """Update an existing novel chapter"""
        try:
            novel.updated_at = datetime.utcnow()
            result = self.collection.update_one(
                {"chapter_number": novel.chapter_number},
                {"$set": novel.to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating novel chapter: {e}")
            return False
    
    def add_link(self, chapter_number: int, link: Link) -> bool:
        """Add a link to a novel chapter"""
        try:
            # Check if link already exists
            novel = self.find_by_chapter_number(chapter_number)
            if novel:
                # Check for duplicate URL
                for existing_link in novel.links:
                    if existing_link.url == link.url:
                        print(f"Link already exists for chapter {chapter_number}")
                        return False
                
                # Add new link
                result = self.collection.update_one(
                    {"chapter_number": chapter_number},
                    {
                        "$push": {"links": link.to_dict()},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
                return result.modified_count > 0
            else:
                # Create new chapter with the link
                new_novel = Novel(
                    chapter_number=chapter_number,
                    links=[link]
                )
                result = self.create(new_novel)
                return result is not None
                
        except Exception as e:
            print(f"Error adding link to novel chapter: {e}")
            return False
    
    def delete_by_chapter_number(self, chapter_number: int) -> bool:
        """Delete a novel chapter"""
        try:
            result = self.collection.delete_one({"chapter_number": chapter_number})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting novel chapter: {e}")
            return False
    
    def count(self) -> int:
        """Count total novel chapters"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting novel chapters: {e}")
            return 0
