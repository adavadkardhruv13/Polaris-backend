import bleach
from html import escape
import magic
from typing import Optional
from .config import settings
from .exceptions import ValidationError
from .logger import logger

class InputValidator:
    @staticmethod
    def validate_pitch_content(pitch:str)->str:
        """validate and sanitize pitch content"""
        if not pitch or not pitch.strip():
            raise ValidationError("Pitch content cannot be empty")
        
        pitch = pitch.strip()
        
        if len(pitch)<settings.min_pitch_length:
            raise ValidationError(f"Pitch content too short. Minimum {settings.min_pitch_length} characters required")
        
        if len(pitch) > settings.max_pitch_length:
            raise ValidationError(f"Pitch content too long. Maximum {settings.max_pitch_length} characters allowed")
        
        
        sanitized = bleach.clean(pitch, tags=[], strip=True)
        sanitized = escape(sanitized)
        
        return sanitized
    
    
    @staticmethod
    def validate_file(file_content: bytes, filename: str) -> None:
        """validate uploaded file"""
        
        if not file_content:
            raise ValidationError("File is empty")
        
        if len(file_content) > settings.max_file_size:
            raise ValidationError(f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB")
        
        
        try:
            file_type = magic.from_buffer(file_content, mime=True)
            if file_type not in settings.allowed_file_types:
                raise ValidationError(f"File type '{file_type}' not allowed. Allowed types: {settings.allowed_file_types}")
        except Exception as e:
            logger.warning(f"Could not determine file type for {filename}: {e}")
            # Fallback to extension check
            if not filename.lower().endswith(('.pdf', '.txt')):
                raise ValidationError("Only PDF and TXT files are allowed")