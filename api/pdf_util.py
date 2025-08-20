from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import pdfplumber
import io
from typing import Optional
from .logger import logger
from .exceptions import PDFProcessingError


class PDFProcessor:
    @staticmethod
    async def extract_text_from_pdf(file_content: bytes, filename: str = "unknown") -> str:
        """Extract text from PDF using multiple fallback methods"""
        logger.info(f"Starting PDF text extraction for file: {filename}") 
        
        #method 1: PyPDF
        
        try:
            logger.debug("Attempting text extraction with PyPDF2")
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            if pdf_reader.is_encrypted:
                raise PDFProcessingError("PDF is encrypted and cannot be processed")
            
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                        logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num} with PyPDF2: {e}")
                    
            text = "\n".join(text_parts).strip()
            if text and len(text) > 50:  # Reasonable minimum
                logger.info(f"Successfully extracted {len(text)} characters using PyPDF2")
                return text
                
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed for {filename}: {e}")
            
            
        #method 2: PyMuPDF
        try:
            logger.debug("Attempting text extraction with PyMuPDF")
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            text_parts = []
            for page_num in range(doc.page_count):
                try:
                    page = doc[page_num]
                    page_text = page.get_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                        logger.debug(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1} with PyMuPDF: {e}")
            
            doc.close()
            text = "\n".join(text_parts).strip()
            if text and len(text) > 50:
                logger.info(f"Successfully extracted {len(text)} characters using PyMuPDF")
                return text
                
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed for {filename}: {e}")
        
        # Method 3: pdfplumber
        try:
            logger.debug("Attempting text extraction with pdfplumber")
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text_parts = []
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(page_text)
                            logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num} with pdfplumber: {e}")
                
                text = "\n".join(text_parts).strip()
                if text and len(text) > 50:
                    logger.info(f"Successfully extracted {len(text)} characters using pdfplumber")
                    return text
                    
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {filename}: {e}")
        
        # If all methods failed
        raise PDFProcessingError(
            f"Could not extract text from PDF '{filename}' using any available method. "
            "The PDF might be image-based, corrupted, or have complex formatting."
        )
        