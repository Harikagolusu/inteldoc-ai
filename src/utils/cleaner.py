import re

def clean_extracted_text(text: str) -> str:
    """
    Cleans extracted text by removing extra whitespaces, fixing broken lines, and filtering OCR noise.
    """
    if not text:
        return ""
        
    # Remove basic OCR noise (non-printable/bizarre characters)
    # Keeping basic ascii, punctuation, and standard alphanumerics
    cleaned_text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
    
    # Fix broken lines (remove single newlines but keep paragraph double newlines)
    cleaned_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned_text)
    
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    
    # Strip leading/trailing whitespaces
    return cleaned_text.strip()