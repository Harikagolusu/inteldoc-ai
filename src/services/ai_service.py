import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

def configure_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable is not set. AI features might fail.")
    else:
        genai.configure(api_key=api_key)

# Configure immediately on load
configure_gemini()

async def analyze_text(text: str) -> Dict[str, Any]:
    """
    Uses Gemini API to generate a concise summary and perform sentiment analysis.
    Truncates text if it's too large to fit in context window.
    """
    default_result = {
        "summary": "AI summary currently unavailable due to missing API key or error.",
        "sentiment": "neutral",
        "category": "Uncategorized",
        "keywords": []
    }

    if not text:
        return {"summary": "No content provided to summarize.", "sentiment": "neutral"}
        
    if not os.environ.get("GEMINI_API_KEY"):
        return default_result

    # Truncate text to a safe length for the prompt (e.g., 50000 characters)
    # Truncate text to a safe length for the prompt to guarantee < 5s execution
    max_length = 4000
    if len(text) > max_length:
        text = text[:max_length] + "... (Text truncated to meet performance constraints)"

    prompt = f"""
    Please read the following text and provide:
    1. A concise summary in 3-4 lines. Do not exceed 4 lines.
    2. The overall sentiment of the text. Choose ONLY one of: 'positive', 'negative', or 'neutral'.
    3. Document category (e.g., Invoice, Report, Resume, Email, Article, General).
    4. Top 3-5 key topics/keywords from the text.

    Return ONLY a valid JSON object with the exact following structure and keys, without markdown formatting or code blocks:
    {{
      "summary": "your concise summary here",
      "sentiment": "positive/negative/neutral",
      "category": "document category",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}

    Text to analyze:
    {text}
    """

    try:
        # We can use gemini-1.5-pro or gemini-2.5-flash. Using the default available ones.
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # We use asyncio.to_thread to wrap the synchronous call and avoid blocking or grpc deadlocks
        import asyncio
        response = await asyncio.to_thread(model.generate_content, prompt)
        content = response.text.strip()
        
        # Clean up potential markdown formatting like ```json ... ```
        if content.startswith("```"):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])
        
        parsed = json.loads(content)
        
        return {
            "summary": parsed.get("summary", "Summary unavailable."),
            "sentiment": parsed.get("sentiment", "neutral").lower(),
            "category": parsed.get("category", "General"),
            "keywords": parsed.get("keywords", [])
        }
        
    except Exception as e:
        logger.error(f"Gemini API call failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return default_result