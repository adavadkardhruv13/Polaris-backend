from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    openai_model: str = "gpt-4.1" 
    
    max_pitch_length: int = 90000
    min_pitch_length: int = 90
    max_file_size: int = 10 * 1024 * 1024 #10MB
    
    allowed_file_type: List[str] = ["application/pdf"]
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    rate_limit: str = "10/minute"
    
    log_level: str = "INFO"
    log_file: str = "pitch_analyzer.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()