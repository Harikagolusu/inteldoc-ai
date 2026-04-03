import io
import pdfplumber
import docx
import logging
from src.services.ocr_service import extract_text_from_image

logger = logging.getLogger(__name__)

async def extract_text_from_file(file_content: bytes, filename: str, content_type: str) -> str:
    """
    Route extraction to appropriate handler based on file type.
    """
    text = ""
    lower_filename = filename.lower()
    
    if content_type == "application/pdf" or lower_filename.endswith(".pdf"):
        text = await _extract_pdf(file_content)
    elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"] or lower_filename.endswith(".docx"):
        text = await _extract_docx(file_content)
    elif content_type.startswith("image/") or lower_filename.endswith((".png", ".jpg", ".jpeg")):
        text = await extract_text_from_image(file_content)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")
        
    return text

async def _extract_pdf(file_content: bytes) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Failed to parse PDF: {str(e)}")
        raise Exception("Failed to read PDF file. It might be corrupted or encrypted.")

async def _extract_docx(file_content: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Failed to parse DOCX: {str(e)}")
        raise Exception("Failed to read DOCX file. It might be corrupted.")