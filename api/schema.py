from pydantic import BaseModel, Field, field_validator
from pydantic.json_schema import GetJsonSchemaHandler, JsonSchemaValue
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId

class SectionFeedback(BaseModel):
    summary: str = Field(..., description="Brief summary of the section")
    feedback: str = Field(..., description="Detailed feedback and recommendations")
    score: Optional[int] = Field(None, ge=0, le=100, description="Section score out of 100")

class PitchFeedback(BaseModel):
    # Analysis metadata
    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="Analysis processing time in seconds")
    
    # Section analyses
    problem: SectionFeedback
    solution: SectionFeedback
    market_size: SectionFeedback
    business_model: SectionFeedback
    go_to_market_strategy: SectionFeedback
    traction: SectionFeedback
    team: SectionFeedback
    competitive_advantage: SectionFeedback
    vision: SectionFeedback

    # Scoring
    scores: Dict[str, int] = Field(..., description="Overall scores for different aspects")

    # Additional insights
    investor_questions: List[str] = Field(..., description="Top questions investors might ask")
    overall_impression: str = Field(..., description="Overall assessment of the pitch")
    
    # Enhanced features
    content_statistics: Optional[Dict[str, Any]] = Field(None, description="Basic content statistics")
    risk_factors: Optional[List[str]] = Field(None, description="Potential risk factors identified")
    strengths: Optional[List[str]] = Field(None, description="Key strengths identified")

class PitchRequest(BaseModel):
    pitch: str = Field(..., min_length=1, max_length=50000, description="Pitch content to analyze")

class AnalysisResponse(BaseModel):
    status: str
    analysis: PitchFeedback
    cache_hit: bool = False
    processing_time: float

class ErrorResponse(BaseModel):
    status: str = "error"
    error_type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: Any, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Generate base schema
        schema = handler(core_schema)
        # Modify to show as string instead of ObjectId
        schema.update(type="string")
        return schema
        
class InvestorBase(BaseModel):
    """Base model for investor data"""
    Investor_name: str = Field(..., description="Investor name")
    Investor_type: Optional[str] = Field(None, description="Investor type (VC, Angel, PE, etc.)")
    Global_HQ: Optional[str] = Field(None, description="Location/Country")
    Stage_of_investment: Optional[str] = Field(None, description="Investment stage (Seed, Series A, etc.)")
    Website: Optional[str] = Field(None, description="Website URL")
    
    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True
    }


class InvestorInDB(InvestorBase):
    """Investor model for database storage"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
        "populate_by_name": True
    }


class InvestorResponse(BaseModel):
    """Investor model for API responses"""
    id: str = Field(..., description="Investor ID")
    Investor_name: str = Field(..., description="Investor name")
    Investor_type: Optional[str] = Field(None, description="Investor type")
    Global_HQ: Optional[str] = Field(None, description="Location/Country")
    Stage_of_investment: Optional[str] = Field(None, description="Investment stage")
    Website: Optional[str] = Field(None, description="Website URL")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "json_encoders": {ObjectId: str},
        "from_attributes": True
    }


class InvestorListResponse(BaseModel):
    """Response model for paginated investor list"""
    investors: List[InvestorResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class InvestorFilters(BaseModel):
    """Model for investor filtering parameters"""
    search: Optional[str] = Field(None, description="Search in name, description, sectors")
    type: Optional[str] = Field(None, description="Filter by investor type")
    location: Optional[str] = Field(None, description="Filter by location")
    investment_stage: Optional[str] = Field(None, description="Filter by investment stage")


class InvestorCreate(BaseModel):
    """Model for creating new investors"""
    Investor_name: str = Field(..., description="Investor name")
    Investor_type: Optional[str] = Field(None, description="Investor type")
    Global_HQ: Optional[str] = Field(None, description="Location/Country")
    Stage_of_investment: Optional[str] = Field(None, description="Investment stage")
    Website: Optional[str] = Field(None, description="Website URL")


class InvestorUpdate(BaseModel):
    """Model for updating investors"""
    Investor_name: Optional[str] = Field(None, description="Investor name")
    Investor_type: Optional[str] = Field(None, description="Investor type")
    Global_HQ: Optional[str] = Field(None, description="Location/Country")
    Stage_of_investment: Optional[str] = Field(None, description="Investment stage")
    Website: Optional[str] = Field(None, description="Website URL")