class PitchAnalyzerException(Exception):
    """Base exception for pitch analyzer"""
    pass

class ValidationError(PitchAnalyzerException):
    """Raised when input validation fails"""
    pass

class PDFProcessingError(PitchAnalyzerException):
    """Raised when PDF processing fails"""
    pass

class AnalysisError(PitchAnalyzerException):
    """Raised when AI analysis fails"""
    pass

class RateLimitError(PitchAnalyzerException):
    """Raised when rate limit is exceeded"""
    pass