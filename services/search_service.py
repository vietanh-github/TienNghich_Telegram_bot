"""
Search service
Business logic for searching novels and episodes
"""
from typing import Tuple, List, Dict, Any
from repositories import NovelRepository, EpisodeRepository, MappingRepository
from database.models import Novel, Episode, Mapping
from utils.constants import SEARCH_TYPE_CHAPTER, SEARCH_TYPE_3D, SEARCH_TYPE_2D


class SearchService:
    """Service for search operations"""
    
    def __init__(self):
        self.novel_repo = NovelRepository()
        self.episode_3d_repo = EpisodeRepository("3d")
        self.episode_2d_repo = EpisodeRepository("2d")
        self.mapping_repo = MappingRepository()
    
    def search_by_chapter(self, chapter_number: int) -> Dict[str, Any]:
        """
        Search by chapter number
        Returns related novels, 3D episodes, 2D episodes, and mappings
        """
        try:
            # Find the novel chapter
            novel = self.novel_repo.find_by_chapter_number(chapter_number)
            novels = [novel] if novel else []
            
            # Find mappings that include this chapter
            mappings = self.mapping_repo.find_by_chapter(chapter_number)
            
            # If no novel doc but mapping exists, create placeholder
            if not novels and mappings:
                novels.append(Novel(chapter_number=chapter_number))
            
            # Extract unique episode numbers
            episode_3d_numbers = set()
            episode_2d_numbers = set()
            
            for mapping in mappings:
                if mapping.episode_3d:
                    episode_3d_numbers.add(mapping.episode_3d)
                if mapping.episode_2d:
                    episode_2d_numbers.add(mapping.episode_2d)
            
            # Find episodes
            episodes_3d = []
            if episode_3d_numbers:
                found = self.episode_3d_repo.find_by_episode_numbers(list(episode_3d_numbers))
                episodes_3d.extend(found)
                # Add placeholders for missing
                found_ids = {e.episode_number for e in found}
                for num in episode_3d_numbers:
                    if num not in found_ids:
                        episodes_3d.append(Episode(episode_number=num))
            
            episodes_2d = []
            if episode_2d_numbers:
                found = self.episode_2d_repo.find_by_episode_numbers(list(episode_2d_numbers))
                episodes_2d.extend(found)
                # Add placeholders
                found_ids = {e.episode_number for e in found}
                for num in episode_2d_numbers:
                    if num not in found_ids:
                        episodes_2d.append(Episode(episode_number=num))
            
            return {
                "novels": novels,
                "episodes_3d": episodes_3d,
                "episodes_2d": episodes_2d,
                "mappings": mappings,
                "search_type": SEARCH_TYPE_CHAPTER,
                "search_value": chapter_number
            }
            
        except Exception as e:
            print(f"Error in search_by_chapter: {e}")
            return {
                "novels": [],
                "episodes_3d": [],
                "episodes_2d": [],
                "mappings": [],
                "search_type": SEARCH_TYPE_CHAPTER,
                "search_value": chapter_number
            }
    
    def search_by_episode_3d(self, episode_number: int) -> Dict[str, Any]:
        """
        Search by 3D episode number
        Returns related novels, episodes, and mappings
        """
        try:
            # Find the episode
            episode = self.episode_3d_repo.find_by_episode_number(episode_number)
            episodes_3d = [episode] if episode else []
            
            # Find mapping for this episode
            mapping = self.mapping_repo.find_by_episode_3d(episode_number)
            mappings = [mapping] if mapping else []
            
            # If no episode doc but mapping exists, create placeholder
            if not episodes_3d and mapping:
                episodes_3d.append(Episode(episode_number=episode_number))
            
            # Find related chapters and 2D episode
            novels = []
            episodes_2d = []
            
            if mapping:
                # Find novel chapters
                if mapping.novel_chapters:
                    found = self.novel_repo.find_by_chapter_numbers(mapping.novel_chapters)
                    novels.extend(found)
                    # Add placeholders
                    found_ids = {n.chapter_number for n in found}
                    for num in mapping.novel_chapters:
                        if num not in found_ids:
                            novels.append(Novel(chapter_number=num))
                
                # Find 2D episode if exists
                if mapping.episode_2d:
                    episode_2d = self.episode_2d_repo.find_by_episode_number(mapping.episode_2d)
                    if episode_2d:
                        episodes_2d = [episode_2d]
                    else:
                        episodes_2d.append(Episode(episode_number=mapping.episode_2d))
            
            return {
                "novels": novels,
                "episodes_3d": episodes_3d,
                "episodes_2d": episodes_2d,
                "mappings": mappings,
                "search_type": SEARCH_TYPE_3D,
                "search_value": episode_number
            }
            
        except Exception as e:
            print(f"Error in search_by_episode_3d: {e}")
            return {
                "novels": [],
                "episodes_3d": [],
                "episodes_2d": [],
                "mappings": [],
                "search_type": SEARCH_TYPE_3D,
                "search_value": episode_number
            }
    
    def search_by_episode_2d(self, episode_number: int) -> Dict[str, Any]:
        """
        Search by 2D episode number
        Returns related novels, episodes, and mappings
        """
        try:
            # Find the episode
            episode = self.episode_2d_repo.find_by_episode_number(episode_number)
            episodes_2d = [episode] if episode else []
            
            # Find mapping for this episode
            mapping = self.mapping_repo.find_by_episode_2d(episode_number)
            mappings = [mapping] if mapping else []
            
            # If no episode doc but mapping exists, placeholder
            if not episodes_2d and mapping:
                episodes_2d.append(Episode(episode_number=episode_number))
            
            # Find related chapters and 3D episode
            novels = []
            episodes_3d = []
            
            if mapping:
                # Find novel chapters
                if mapping.novel_chapters:
                    found = self.novel_repo.find_by_chapter_numbers(mapping.novel_chapters)
                    novels.extend(found)
                    # Placeholders
                    found_ids = {n.chapter_number for n in found}
                    for num in mapping.novel_chapters:
                        if num not in found_ids:
                            novels.append(Novel(chapter_number=num))
                
                # Find 3D episode if exists
                if mapping.episode_3d:
                    episode_3d = self.episode_3d_repo.find_by_episode_number(mapping.episode_3d)
                    if episode_3d:
                        episodes_3d = [episode_3d]
                    else:
                        episodes_3d.append(Episode(episode_number=mapping.episode_3d))
            
            return {
                "novels": novels,
                "episodes_3d": episodes_3d,
                "episodes_2d": episodes_2d,
                "mappings": mappings,
                "search_type": SEARCH_TYPE_2D,
                "search_value": episode_number
            }
            
        except Exception as e:
            print(f"Error in search_by_episode_2d: {e}")
            return {
                "novels": [],
                "episodes_3d": [],
                "episodes_2d": [],
                "mappings": [],
                "search_type": SEARCH_TYPE_2D,
                "search_value": episode_number
            }
    
    def get_full_list(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get full list of mappings with details
        Sorted by 3D episode desc
        """
        try:
            mappings = self.mapping_repo.get_all_mappings_sorted(limit, offset)
            result = []
            
            for mapping in mappings:
                item = {
                    "mapping": mapping,
                    "episode_3d": None,
                    "episode_2d": None,
                    "novel": None
                }
                
                # Fetch details
                if mapping.episode_3d:
                    item["episode_3d"] = self.episode_3d_repo.find_by_episode_number(mapping.episode_3d)
                
                if mapping.episode_2d:
                    item["episode_2d"] = self.episode_2d_repo.find_by_episode_number(mapping.episode_2d)
                
                if mapping.novel_chapters:
                    # Just get the first chapter for link purposes
                    item["novel"] = self.novel_repo.find_by_chapter_number(mapping.novel_chapters[0])
                    
                result.append(item)
                
            return result
        except Exception as e:
            print(f"Error getting full list: {e}")
            return []
