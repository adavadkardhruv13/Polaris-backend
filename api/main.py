from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Depends, Query
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import traceback
from datetime import datetime
from .config import settings
from .logger import logger
from .exceptions import PDFProcessingError, PitchAnalyzerException, ValidationError, RateLimitError, AnalysisError
from .pitch_analyzer import pitch_analyzer, PitchAnalyzer, PitchFeedback
from .pdf_util import PDFProcessingError, PDFProcessor
from .schema import PitchFeedback, PitchRequest, AnalysisResponse, ErrorResponse, InvestorListResponse, InvestorResponse, InvestorInDB, InvestorFilters, InvestorBase
from .validators import InputValidator
from .investor_service import investor_service
from .database import connect_to_mongo, close_mongo_connection

# Initialize FastAPI app
app = FastAPI(
    title="Polaris",
    description="Robust AI-powered pitch deck analysis and Investor info service",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ANALYSIS_COUNT = Counter('pitch_analyses_total', 'Total pitch analyses', ['type', 'status'])
PDF_PROCESSING_DURATION = Histogram('pdf_processing_duration_seconds', 'PDF processing duration')

# Middleware for metrics and logging
@app.middleware("http")
async def add_metrics_and_logging(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)} - {duration:.3f}s")
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=500
        ).inc()
        raise
    
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error_type="ValidationError",
            message=str(exc)
        ).dict()
    )

@app.exception_handler(PDFProcessingError)
async def pdf_processing_exception_handler(request: Request, exc: PDFProcessingError):
    logger.error(f"PDF processing error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_type="PDFProcessingError",
            message=str(exc)
        ).dict()
    )

@app.exception_handler(AnalysisError)
async def analysis_exception_handler(request: Request, exc: AnalysisError):
    logger.error(f"Analysis error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_type="AnalysisError",
            message="Analysis service temporarily unavailable. Please try again later."
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_type="InternalServerError",
            message="An unexpected error occurred. Please try again later."
        ).dict()
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test AI service (simple call)
        test_result = await pitch_analyzer.llm.ainvoke("test")
        ai_status = "healthy"
    except Exception as e:
        logger.warning(f"AI service health check failed: {e}")
        ai_status = "unhealthy"
    
    # # Test cache
    # cache_status = "healthy" if cache_manager.redis_client else "disabled"
    
    # return {
    #     "status": "healthy",
    #     "timestamp": datetime.utcnow().isoformat(),
    #     "version": "2.0.0",
    #     "services": {
    #         "ai_service": ai_status,
    #         "cache": cache_status
    #     }
    # }

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Main analysis endpoints
@app.post("/analyze_pitch", response_model=AnalysisResponse)
@limiter.limit(settings.rate_limit)
async def analyze_pitch_text(request: Request, data: PitchRequest):
    """Analyze pitch deck from text content"""
    start_time = time.time()
    
    try:
        # Validate input
        validated_pitch = InputValidator.validate_pitch_content(data.pitch)
        logger.info(f"Starting text pitch analysis - Length: {len(validated_pitch)} chars")
        
        # Analyze pitch
        result = await pitch_analyzer.analyze_pitch(validated_pitch)
        
        # Record metrics
        ANALYSIS_COUNT.labels(type="text", status="success").inc()
        
        processing_time = round(time.time() - start_time, 2)
        
        return AnalysisResponse(
            status="success",
            analysis=PitchFeedback(**result),
            processing_time=processing_time
        )
        
    except (ValidationError, PDFProcessingError, AnalysisError) as e:
        ANALYSIS_COUNT.labels(type="text", status="error").inc()
        raise e
    except Exception as e:
        ANALYSIS_COUNT.labels(type="text", status="error").inc()
        logger.error(f"Unexpected error in text analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis service temporarily unavailable")

@app.post("/analyze_pdf", response_model=AnalysisResponse)
@limiter.limit(settings.rate_limit)
async def analyze_pitch_pdf(request: Request, file: UploadFile = File(...)):
    """Analyze pitch deck from PDF file"""
    start_time = time.time()
    
    try:
        # Read and validate file
        file_content = await file.read()
        InputValidator.validate_file(file_content, file.filename or "unknown.pdf")
        
        logger.info(f"Starting PDF pitch analysis - File: {file.filename}, Size: {len(file_content)} bytes")
        
        # Extract text from PDF
        pdf_start_time = time.time()
        extracted_text = await PDFProcessor.extract_text_from_pdf(file_content, file.filename)
        pdf_processing_time = time.time() - pdf_start_time
        
        PDF_PROCESSING_DURATION.observe(pdf_processing_time)
        logger.info(f"PDF text extraction completed in {pdf_processing_time:.2f}s - Extracted {len(extracted_text)} characters")
        
        # Validate extracted text
        validated_text = InputValidator.validate_pitch_content(extracted_text)
        
        # Analyze pitch
        result = await pitch_analyzer.analyze_pitch(validated_text)
        
        # Record metrics
        ANALYSIS_COUNT.labels(type="pdf", status="success").inc()
        
        processing_time = round(time.time() - start_time, 2)
        
        return AnalysisResponse(
            status="success",
            analysis=PitchFeedback(**result),
            processing_time=processing_time
        )
        
    except (ValidationError, PDFProcessingError, AnalysisError) as e:
        ANALYSIS_COUNT.labels(type="pdf", status="error").inc()
        raise e
    except Exception as e:
        ANALYSIS_COUNT.labels(type="pdf", status="error").inc()
        logger.error(f"Unexpected error in PDF analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis service temporarily unavailable")
    
    
@app.get("/investors", response_model=InvestorListResponse)
async def get_investors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in name, description, sectors"),
    type: Optional[str] = Query(None, description="Filter by investor type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    investment_stage: Optional[str] = Query(None, description="Filter by investment stage"),
    sort_by: str = Query("Investor_name", description="Sort field"),  # Updated default
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")
):
    """Get investors with pagination and filters"""
    try:
        filters = InvestorFilters(
            search=search,
            type=type,
            location=location,
            investment_stage=investment_stage,
        )
        
        sort_order_int = 1 if sort_order == "asc" else -1
        
        result = await investor_service.get_investors(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order_int
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching investors: {e}")
        raise HTTPException(status_code=500, detail="Error fetching investors")

@app.get("/investors/{investor_id}", response_model=InvestorResponse)
async def get_investor(investor_id: str):
    """Get investor by ID"""
    try:
        investor = await investor_service.get_investor_by_id(investor_id)
        if not investor:
            raise HTTPException(status_code=404, detail="Investor not found")
        
        return investor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching investor {investor_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching investor")

# Additional utility endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "AI Pitch Deck Analyzer",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "analyze_text": "/analyze_pitch",
            "analyze_pdf": "/analyze_pdf",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level=settings.log_level.lower()
    )