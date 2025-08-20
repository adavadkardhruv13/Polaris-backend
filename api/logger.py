<<<<<<< HEAD
import logging
import sys
from pathlib import Path
from datetime import datetime
from .config import settings



def setup_logger():
    """Setup application logger with file and console handlers"""
    
    logger = logging.getLogger("pitch_analyzer")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"{datetime.now().strftime('%Y-%m-%d')}_{settings.log_file}"
    )
    
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
=======
import logging
import sys
from pathlib import Path
from datetime import datetime
from .config import settings



def setup_logger():
    """Setup application logger with file and console handlers"""
    
    logger = logging.getLogger("pitch_analyzer")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"{datetime.now().strftime('%Y-%m-%d')}_{settings.log_file}"
    )
    
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
>>>>>>> c72182e161d21bf2b9034ca62c709ac59f608736
