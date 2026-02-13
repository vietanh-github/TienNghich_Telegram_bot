import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load env variables (assuming .env has local config)
load_dotenv()

# Configuration
LOCAL_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
LOCAL_DB_NAME = os.getenv("MONGODB_DATABASE", "tien_nghich_bot")

async def migrate_data(cloud_uri):
    """
    Migrate data from local MongoDB to Cloud MongoDB
    """
    print(f"🔌 Connecting to LOCAL DB: {LOCAL_URI}...")
    local_client = AsyncIOMotorClient(LOCAL_URI)
    local_db = local_client[LOCAL_DB_NAME]
    
    print(f"🔌 Connecting to CLOUD DB...")
    try:
        cloud_client = AsyncIOMotorClient(cloud_uri)
        # Check connection
        await cloud_client.admin.command('ping')
        print("✅ Connected to Cloud DB successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to Cloud DB: {e}")
        return

    cloud_db = cloud_client[LOCAL_DB_NAME]
    
    # Get all collection names
    collections = await local_db.list_collection_names()
    print(f"📂 Found collections: {collections}")
    
    for col_name in collections:
        print(f"\n🔄 Migrating collection: {col_name}...")
        local_col = local_db[col_name]
        cloud_col = cloud_db[col_name]
        
        # Get all documents
        cursor = local_col.find({})
        docs = await cursor.to_list(length=None)
        
        if not docs:
            print(f"   ⚠️ Collection {col_name} is empty. Skipping.")
            continue
            
        print(f"   📄 Found {len(docs)} documents.")
        
        # Insert into cloud (using insert_many for speed, handling duplicates?)
        # For simplicity in migration, we can drop and recreate or upsert.
        # Let's try insert_many with ordered=False to continue on error (duplicates)
        try:
            result = await cloud_col.insert_many(docs, ordered=False)
            print(f"   ✅ Inserted {len(result.inserted_ids)} documents.")
        except Exception as e:
            # pymongo.errors.BulkWriteError
            inserted = e.details.get('nInserted', 0)
            print(f"   ⚠️ Inserted {inserted} documents (some may be duplicates). Error: {e}")
            
    print("\n🎉 Migration completed!")
    local_client.close()
    cloud_client.close()

if __name__ == "__main__":
    print("🚀 MONGODB MIGRATION TOOL")
    print("--------------------------------")
    print(f"Source: {LOCAL_URI} ({LOCAL_DB_NAME})")
    
    cloud_uri = input("\n👉 Nhập Connection String của MongoDB Atlas (Cloud):\n(Ví dụ: mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority)\n> ").strip()
    
    if not cloud_uri:
        print("❌ Connection string cannot be empty.")
        exit(1)
        
    asyncio.run(migrate_data(cloud_uri))
