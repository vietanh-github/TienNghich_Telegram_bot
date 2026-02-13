
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_db
from repositories.episode_repository import EpisodeRepository
from repositories.novel_repository import NovelRepository
from database.models import Episode, Novel, Link

def import_3d_data():
    """Import 3D episodes from JSON"""
    json_path = "tien_nghich_3d.json"
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    print(f"Reading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    repo = EpisodeRepository(episode_type="3d")
    count = 0
    updated = 0
    
    print(f"Found {len(data)} items. Starting import...")
    
    for item in data:
        number = item.get('number')
        url = item.get('url')
        
        if not number or not url:
            continue
            
        # Check if episode exists
        existing = repo.find_by_episode_number(number)
        
        if existing:
            # Check if link exists
            has_link = False
            if existing.links:
                for link in existing.links:
                    if link.url == url:
                        has_link = True
                        break
            
            if not has_link:
                # Add link
                repo.add_link(number, Link(url=url, source_name="Tram3D"))
                updated += 1
                print(f"Updated 3D Episode {number}")
        else:
            # Create new
            episode = Episode(
                episode_number=number,
                title=f"Tập {number}",
                links=[Link(url=url, source_name="Tram3D")]
            )
            repo.create(episode)
            count += 1
            print(f"Created 3D Episode {number}")

    print(f"3D Import finished: {count} created, {updated} updated.")


def import_chapter_data():
    """Import novel chapters from JSON"""
    json_path = "tien_nghich_chapters.json"
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    print(f"Reading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    repo = NovelRepository()
    count = 0
    updated = 0
    
    print(f"Found {len(data)} items. Starting import...")
    
    for item in data:
        number = item.get('number')
        url = item.get('url')
        title = item.get('title', '')
        
        if not number or not url:
            continue
            
        # Check if chapter exists
        existing = repo.find_by_chapter_number(number)
        
        if existing:
            # Check if link exists
            has_link = False
            if existing.links:
                for link in existing.links:
                    if link.url == url:
                        has_link = True
                        break
            
            if not has_link:
                repo.add_link(number, Link(url=url, source_name="TruyenFull"))
                updated += 1
                # print(f"Updated Chapter {number}")
        else:
            # Create new
            novel = Novel(
                chapter_number=number,
                title=title,
                links=[Link(url=url, source_name="TruyenFull")]
            )
            repo.create(novel)
            count += 1
            # print(f"Created Chapter {number}")
            
        if count % 100 == 0:
            print(f"Processed {count} chapters...")

    print(f"Chapter Import finished: {count} created, {updated} updated.")

if __name__ == "__main__":
    db = get_db()
    print("Database connected.")
    
    import_3d_data()
    import_chapter_data()
    
    print("Import completed.")
