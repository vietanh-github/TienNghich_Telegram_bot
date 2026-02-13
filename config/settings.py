"""
Configuration settings management
Loads environment variables and provides configuration access
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Admin Configuration
    ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'tien_nghich_bot')
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")
        
        if cls.ADMIN_ID == 0:
            raise ValueError("ADMIN_ID is required in .env file")
        
        return True


# Create singleton instance
settings = Settings()
