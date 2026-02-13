"""
Episode repository
Handles database operations for 3D and 2D episodes
"""
from typing import Optional, List
from database.connection import get_db
from database.models import Episode, Link
from datetime import datetime


class EpisodeRepository:
    """Repository for episodes (both 3D and 2D)"""
    
    def __init__(self, episode_type: str):
        """
        Initialize repository
        
        Args:
            episode_type: "3d" or "2d"
        """
        self.db = get_db()
        self.episode_type = episode_type
        
        if episode_type == "3d":
            self.collection = self.db.episodes_3d
        elif episode_type == "2d":
            self.collection = self.db.episodes_2d
        else:
            raise ValueError("episode_type must be '3d' or '2d'")
    
    def find_by_episode_number(self, episode_number: int) -> Optional[Episode]:
        """Find episode by episode number"""
        try:
            data = self.collection.find_one({"episode_number": episode_number})
            if data:
                return Episode.from_dict(data)
            return None
        except Exception as e:
            print(f"Error finding {self.episode_type} episode: {e}")
            return None
    
    def find_by_episode_numbers(self, episode_numbers: List[int]) -> List[Episode]:
        """Find multiple episodes by episode numbers"""
        try:
            cursor = self.collection.find(
                {"episode_number": {"$in": episode_numbers}}
            ).sort("episode_number", 1)
            
            return [Episode.from_dict(data) for data in cursor]
        except Exception as e:
            print(f"Error finding {self.episode_type} episodes: {e}")
            return []
    
    def create(self, episode: Episode) -> Optional[Episode]:
        """Create a new episode"""
        try:
            # Check if episode already exists
            existing = self.find_by_episode_number(episode.episode_number)
            if existing:
                print(f"{self.episode_type.upper()} episode {episode.episode_number} already exists")
                return existing
            
            result = self.collection.insert_one(episode.to_dict())
            episode._id = result.inserted_id
            return episode
        except Exception as e:
            print(f"Error creating {self.episode_type} episode: {e}")
            return None
    
    def update(self, episode: Episode) -> bool:
        """Update an existing episode"""
        try:
            episode.updated_at = datetime.utcnow()
            result = self.collection.update_one(
                {"episode_number": episode.episode_number},
                {"$set": episode.to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating {self.episode_type} episode: {e}")
            return False
    
    def add_link(self, episode_number: int, link: Link) -> bool:
        """Add a link to an episode"""
        try:
            # Check if link already exists
            episode = self.find_by_episode_number(episode_number)
            if episode:
                # Check for duplicate URL
                for existing_link in episode.links:
                    if existing_link.url == link.url:
                        print(f"Link already exists for {self.episode_type} episode {episode_number}")
                        return False
                
                # Add new link
                result = self.collection.update_one(
                    {"episode_number": episode_number},
                    {
                        "$push": {"links": link.to_dict()},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
                return result.modified_count > 0
            else:
                # Create new episode with the link
                new_episode = Episode(
                    episode_number=episode_number,
                    links=[link]
                )
                result = self.create(new_episode)
                return result is not None
                
        except Exception as e:
            print(f"Error adding link to {self.episode_type} episode: {e}")
            return False
    
    def delete_by_episode_number(self, episode_number: int) -> bool:
        """Delete an episode"""
        try:
            result = self.collection.delete_one({"episode_number": episode_number})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting {self.episode_type} episode: {e}")
            return False
    
    def count(self) -> int:
        """Count total episodes"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting {self.episode_type} episodes: {e}")
            return 0
