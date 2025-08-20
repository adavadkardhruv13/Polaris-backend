<<<<<<< HEAD
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

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
=======
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

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
>>>>>>> c72182e161d21bf2b9034ca62c709ac59f608736
    timestamp: datetime = Field(default_factory=datetime.utcnow)