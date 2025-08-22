from .database import get_database
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional, Dict, Any
from .logger import logger
import re, math
from bson import ObjectId
from datetime import datetime
from .schema import InvestorInDB, InvestorResponse, InvestorFilters, InvestorListResponse


class InvestorService:
    
    def __init__(self):
        self.collection_name = 'investors'
        
        
    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get the investors collection"""
        db = await get_database()
        return db[self.collection_name]
    
    async def create_investor(self, investor_data: Dict[str, Any]) -> str:
        """Create a new investor"""
        collection = await self.get_collection()
        
        try:
            # Add timestamps
            investor_data['created_at'] = datetime.utcnow()
            investor_data['updated_at'] = datetime.utcnow()
            
            # Create the investor document
            investor = InvestorInDB(**investor_data)
            
            # Convert to dict and handle ObjectId
            investor_dict = investor.model_dump(by_alias=True, exclude_unset=True)
            
            # Insert into database
            result = await collection.insert_one(investor_dict)
            logger.info(f"Created investor: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating investor: {e}")
            raise

    async def bulk_create_investors(self, investors_data: List[Dict[str, Any]]) -> int:
        """Bulk create investors from CSV data"""
        collection = await self.get_collection()
        
        investors = []
        for data in investors_data:
            try:
                # Add timestamps
                data['created_at'] = datetime.utcnow()
                data['updated_at'] = datetime.utcnow()
                
                # Create investor model
                investor = InvestorInDB(**data)
                investor_dict = investor.model_dump(by_alias=True, exclude_unset=True)
                investors.append(investor_dict)
                
            except Exception as e:
                logger.warning(f"Skipping invalid investor data: {e}")
                continue
        
        if investors:
            try:
                result = await collection.insert_many(investors)
                logger.info(f"Bulk created {len(result.inserted_ids)} investors")
                return len(result.inserted_ids)
            except Exception as e:
                logger.error(f"Error in bulk insert: {e}")
                raise
        
        return 0
    
    async def get_investors(
        self, 
        page: int = 1,
        page_size: int = 20,
        filters: Optional[InvestorFilters] = None,
        sort_by: str = 'Investor_name',
        sort_order: int = 1,
    ) -> InvestorListResponse:
        """Get paginated list of investors with filters"""
        collection = await self.get_collection()
        
        try:
            # Build query
            query: Dict[str, Any] = {}
            if filters:
                if filters.search:
                    search_regex = re.compile(filters.search, re.IGNORECASE)
                    query["$or"] = [
                        {"Investor_name": search_regex},
                        {"Investor_type": search_regex},
                        {"Global_HQ": search_regex},
                        {"Stage_of_investment": search_regex}
                    ]
                    
                if filters.type:
                    query["Investor_type"] = re.compile(filters.type, re.IGNORECASE)
                    
                if filters.location:
                    query["Global_HQ"] = re.compile(filters.location, re.IGNORECASE)
            
                if filters.investment_stage:
                    query["Stage_of_investment"] = re.compile(filters.investment_stage, re.IGNORECASE)
            
            # Count total documents matching the query
            total_count = await collection.count_documents(query)
            
            # Calculate pagination
            total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1
            skip = (page - 1) * page_size
            
            # Execute the query with pagination and sorting
            cursor = collection.find(query).sort(sort_by, sort_order).skip(skip).limit(page_size)
            documents = await cursor.to_list(length=page_size)
            
            # Convert documents to response models
            investors = []
            for doc in documents:
                try:
                    # Convert ObjectId to string
                    doc["id"] = str(doc["_id"])
                    
                    # Remove the _id field to avoid conflicts
                    if "_id" in doc:
                        del doc["_id"]
                    
                    # Create response model
                    investor_response = InvestorResponse(**doc)
                    investors.append(investor_response)
                    
                except Exception as e:
                    logger.warning(f"Error creating InvestorResponse for doc {doc.get('_id', 'unknown')}: {e}")
                    continue
                
            return InvestorListResponse(
                investors=investors,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            )
            
        except Exception as e:
            logger.error(f"Error getting investors: {e}")
            raise
        
    async def get_investor_by_id(self, investor_id: str) -> Optional[InvestorResponse]:
        """Get investor by ID"""
        collection = await self.get_collection()
        
        try:
            # Validate ObjectId
            if not ObjectId.is_valid(investor_id):
                logger.warning(f"Invalid ObjectId: {investor_id}")
                return None
                
            doc = await collection.find_one({"_id": ObjectId(investor_id)})
            if doc:
                # Convert ObjectId to string
                doc["id"] = str(doc["_id"])
                
                # Remove the _id field
                if "_id" in doc:
                    del doc["_id"]
                
                return InvestorResponse(**doc)
                
        except Exception as e:
            logger.error(f"Error fetching investor {investor_id}: {e}")
        
        return None    
    
    async def update_investor(self, investor_id: str, update_data: Dict[str, Any]) -> bool:
        """Update investor"""
        collection = await self.get_collection()
        
        try:
            # Validate ObjectId
            if not ObjectId.is_valid(investor_id):
                logger.warning(f"Invalid ObjectId: {investor_id}")
                return False
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Remove any None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = await collection.update_one(
                {"_id": ObjectId(investor_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated investor: {investor_id}")
            else:
                logger.warning(f"No changes made to investor: {investor_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error updating investor {investor_id}: {e}")
            return False
    
    async def delete_investor(self, investor_id: str) -> bool:
        """Delete investor"""
        collection = await self.get_collection()
        
        try:
            # Validate ObjectId
            if not ObjectId.is_valid(investor_id):
                logger.warning(f"Invalid ObjectId: {investor_id}")
                return False
                
            result = await collection.delete_one({"_id": ObjectId(investor_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted investor: {investor_id}")
            else:
                logger.warning(f"Investor not found for deletion: {investor_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error deleting investor {investor_id}: {e}")
            return False
        
        
# Create service instance
investor_service = InvestorService()