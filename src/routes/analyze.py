import os
import logging
from fastapi import APIRouter, Header, HTTPException, Depends, UploadFile, File, Request
from pydantic import BaseModel

from src.services.extractor import extract_text_from_file
from src.utils.cleaner import clean_extracted_text
from src.services.ai_service import analyze_text, configure_gemini

router = APIRouter()
logger = logging.getLogger(__name__)

# Fallback response for edge cases/errors
def get_fallback_response():
    return {
        "file_type": "unknown",
        "summary": "Error processing document",
        "entities": {
            "persons": [],
            "organizations": [],
            "dates": [],
            "money": [],
            "locations": []
        },
        "sentiment": "neutral"
    }

def verify_api_key(request: Request):
    # Default to the expected hackathon track key if not explicitly configured in env
    expected_key = os.environ.get("API_KEY", "sk_track2_987654321")
    
    # Check x-api-key header
    x_key = request.headers.get("x-api-key")
    if x_key == expected_key:
        return
        
    # Check Authorization Bearer header
    auth = request.headers.get("authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
        if token == expected_key:
            return
            
    # If neither matches
    raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/analyze")
async def analyze_document(file: UploadFile = File(None), _ = Depends(verify_api_key)):
    """
    Automated Testing Endpoint.
    Analyzes an uploaded document, extracts text, identifies entities, and generates an AI summary with sentiment.
    """
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Trigger AI config loading manually if just started
    configure_gemini()
    
    try:
        # Determine pseudo content type for extractor safely
        filename = getattr(file, "filename", "") or ""
        ft = filename.lower()
        if ft.endswith(".pdf") or getattr(file, "content_type", "") == "application/pdf":
            content_type = "application/pdf"
            file_type_str = "pdf"
        elif ft.endswith(".docx") or "wordprocessingml" in (getattr(file, "content_type", "") or ""):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            file_type_str = "docx"
        elif ft.endswith((".jpg", ".jpeg", ".png")) or (getattr(file, "content_type", "") and "image" in getattr(file, "content_type", "")):
            content_type = "image/jpeg"
            file_type_str = "image"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Read the uploaded file chunks into memory buffer
        file_content = await file.read()
        
        # 1. Extract Text
        raw_text = await extract_text_from_file(file_content, filename, content_type)
        
        if not raw_text.strip():
            return {
                "file_type": file_type_str,
                "summary": "No text could be extracted from the provided file.",
                "entities": {
                    "persons": [],
                    "organizations": [],
                    "dates": [],
                    "money": [],
                    "locations": []
                },
                "sentiment": "neutral"
            }
            
        # 2. Clean Text
        cleaned_text = clean_extracted_text(raw_text)
        
        # 3. Process Entities via Local ML (spaCy)
        from src.services.nlp_service import extract_entities
        nlp_entities = await extract_entities(cleaned_text)
        
        # 4. Process AI Summary, Sentiment, & Entities (Gemini)
        ai_result = await analyze_text(cleaned_text)
        gemini_entities = ai_result.get("entities", {})
        
        # Merge dictionaries intelligently eliminating dupes
        merged_entities = {
            "persons": list(set(nlp_entities.get("persons", [])) | set(gemini_entities.get("persons", []))),
            "organizations": list(set(nlp_entities.get("organizations", [])) | set(gemini_entities.get("organizations", []))),
            "dates": list(set(nlp_entities.get("dates", [])) | set(gemini_entities.get("dates", []))),
            "money": list(set(nlp_entities.get("money", [])) | set(gemini_entities.get("money", []))),
            "locations": list(set(nlp_entities.get("locations", [])) | set(gemini_entities.get("locations", [])))
        }
        
        sentiment_val = str(ai_result.get("sentiment", "neutral")).lower()
        if sentiment_val not in ["positive", "negative", "neutral"]:
            sentiment_val = "neutral"
        
        return {
            "file_type": file_type_str,
            "summary": ai_result.get("summary", "Summary unavailable")[:500],
            "entities": merged_entities,
            "sentiment": sentiment_val
        }
        
    except HTTPException:
        # Re-raise standard HTTP exceptions (like 400 Unsupported format) natively
        raise
    except Exception as e:
        logger.error(f"Error during document analysis: {str(e)}")
        # IMPORTANT: Per specifications, do not crash on failure. Return the safe structural fallback block.
        return get_fallback_response()