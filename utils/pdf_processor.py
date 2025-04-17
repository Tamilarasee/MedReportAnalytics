import io
import logging
import PyPDF2
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file
    
    Args:
        pdf_file: A file-like object containing the PDF
        
    Returns:
        str: The extracted text from the PDF
    """
    try:
        # Check if the file is a FileStorage object
        if isinstance(pdf_file, FileStorage):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer for potential future use
        else:
            pdf_bytes = pdf_file.read()
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        logger.debug(f"Successfully extracted {len(text)} characters from PDF")
        
        if not text.strip():
            logger.warning("Extracted text is empty")
            return None
            
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
