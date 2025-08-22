from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings    
import logging

logger = logging.getLogger("pitch_analyzer")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db= None
    
database = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        database.client = AsyncIOMotorClient(settings.mongodb_url)  # Fixed attribute name
        database.db = database.client[settings.database_name]
        logger.info("Connected to MongoDB")
    except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e
        
async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        logger.info("Closed MongoDB connection")
    else:
        logger.warning("No MongoDB connection to close")
        

async def get_database():
    """Get database instance"""
    return database.db
    