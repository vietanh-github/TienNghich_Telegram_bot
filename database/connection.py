"""
MongoDB database connection management
Provides singleton connection to MongoDB
"""
from pymongo import MongoClient
from pymongo.database import Database
from config.settings import settings


class DatabaseConnection:
    """Singleton MongoDB connection manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def connect(self) -> Database:
        """
        Establish connection to MongoDB
        Returns the database instance
        """
        if self._client is None:
            try:
                self._client = MongoClient(settings.MONGODB_URI)
                self._db = self._client[settings.MONGODB_DATABASE]
                
                # Test connection
                self._client.server_info()
                print(f"✅ Connected to MongoDB: {settings.MONGODB_DATABASE}")
                
                # Create indexes
                self._create_indexes()
                
            except Exception as e:
                print(f"❌ Failed to connect to MongoDB: {e}")
                raise
        
        return self._db
    
    def _create_indexes(self):
        """Create database indexes for optimization"""
        try:
            # Novels indexes
            self._db.novels.create_index("chapter_number", unique=True)
            self._db.novels.create_index([("created_at", -1)])
            
            # Episodes 3D indexes
            self._db.episodes_3d.create_index("episode_number", unique=True)
            
            # Episodes 2D indexes
            self._db.episodes_2d.create_index("episode_number", unique=True)
            
            # Mappings indexes
            self._db.mappings.create_index("novel_chapters")
            self._db.mappings.create_index("episode_3d")
            self._db.mappings.create_index("episode_2d")
            
            # Contributions indexes
            self._db.contributions.create_index("status")
            self._db.contributions.create_index("user_id")
            self._db.contributions.create_index([("submitted_at", -1)])
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Error creating indexes: {e}")
    
    def get_database(self) -> Database:
        """Get database instance"""
        if self._db is None:
            return self.connect()
        return self._db
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("✅ MongoDB connection closed")


# Create singleton instance
db_connection = DatabaseConnection()


def get_db() -> Database:
    """Helper function to get database instance"""
    return db_connection.get_database()
