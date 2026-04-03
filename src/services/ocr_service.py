import pytesseract
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_image(file_content: bytes) -> str:
    """Extract text from an image file using Tesseract OCR."""
    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Failed to perform OCR on image: {str(e)}")
        raise Exception("Failed to read image file or OCR failed.")