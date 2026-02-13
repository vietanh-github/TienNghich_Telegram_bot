import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from database.connection import db_connection
from services import SearchService
from database.models import Novel, Episode, Mapping, Link
from utils.formatters import format_search_result

async def verify_3d_search():
    print("🚀 Starting verification for /3d command logic...")
    
    # Connect to DB
    try:
        db_connection.connect()
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return

    # Check if we can write to DB
    db = db_connection.get_database()
    
    # Create test data
    test_episode_num = 10000
    test_chapter_nums = [2001, 2002]
    test_2d_episode_num = 55
    
    print(f"📦 Creating test data for Episode {test_episode_num}...")
    
    # 1. Create Novel Chapters
    for chap_num in test_chapter_nums:
        novel = Novel(
            chapter_number=chap_num,
            title=f"Test Chapter {chap_num}",
            links=[Link("TestNovelSource", f"http://test.com/chap/{chap_num}")]
        )
        db.novels.update_one(
            {"chapter_number": chap_num},
            {"$set": novel.to_dict()},
            upsert=True
        )
        
    # 2. Create 3D Episode
    episode_3d = Episode(
        episode_number=test_episode_num,
        title=f"Test Episode {test_episode_num}",
        links=[Link("Test3DSource", f"http://test.com/3d/{test_episode_num}")]
    )
    db.episodes_3d.update_one(
        {"episode_number": test_episode_num},
        {"$set": episode_3d.to_dict()},
        upsert=True
    )
    
    # 3. Create 2D Episode
    episode_2d = Episode(
        episode_number=test_2d_episode_num,
        title=f"Test 2D Episode {test_2d_episode_num}",
        links=[Link("Test2DSource", f"http://test.com/2d/{test_2d_episode_num}")]
    )
    db.episodes_2d.update_one(
        {"episode_number": test_2d_episode_num},
        {"$set": episode_2d.to_dict()},
        upsert=True
    )
    
    # 4. Create Mapping
    mapping = Mapping(
        novel_chapters=test_chapter_nums,
        episode_3d=test_episode_num,
        episode_2d=test_2d_episode_num
    )
    db.mappings.update_one(
        {"episode_3d": test_episode_num},
        {"$set": mapping.to_dict()},
        upsert=True
    )
    
    print("✅ Test data created successfully")
    
    # Run Search
    print(f"🔍 Searching for 3D Episode {test_episode_num}...")
    service = SearchService()
    result = service.search_by_episode_3d(test_episode_num)
    
    # Verification of logic
    print("\n📊 Verification Logic:")
    
    found_3d = False
    if result["episodes_3d"]:
        ep = result["episodes_3d"][0]
        print(f"✅ Found 3D Episode: {ep.episode_number}")
        found_3d = True
    else:
        print("❌ Failed to find 3D Episode")
        
    found_novel = False
    if result["novels"]:
        print(f"✅ Found {len(result['novels'])} Novel Chapters")
        found_novel = True
    else:
        print("❌ Failed to find Novel Chapters")

    found_2d = False
    if result["episodes_2d"]:
        ep = result["episodes_2d"][0]
        print(f"✅ Found 2D Episode: {ep.episode_number}")
        found_2d = True
    else:
        print("❌ Failed to find 2D Episode")
        
    # Verification of formatting
    print("\n📝 Verification Formatting:")
    formatted_msg = format_search_result(
        novels=result["novels"],
        episodes_3d=result["episodes_3d"],
        episodes_2d=result["episodes_2d"],
        mappings=result["mappings"],
        search_type=result["search_type"],
        search_value=result["search_value"]
    )
    
    print("-" * 20)
    print(formatted_msg)
    print("-" * 20)
    
    if "Link đọc:" in formatted_msg and "Link xem:" in formatted_msg:
         print("✅ Formatted message contains links")
    else:
         print("❌ Formatted message missing links")

    # Cleanup
    print("\n🧹 Cleaning up test data...")
    db.novels.delete_many({"chapter_number": {"$in": test_chapter_nums}})
    db.episodes_3d.delete_one({"episode_number": test_episode_num})
    db.episodes_2d.delete_one({"episode_number": test_2d_episode_num})
    db.mappings.delete_one({"episode_3d": test_episode_num})
    print("✅ Cleanup complete")
    
    db_connection.close()

if __name__ == "__main__":
    asyncio.run(verify_3d_search())
