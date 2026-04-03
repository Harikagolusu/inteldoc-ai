import asyncio
import os
import io
import base64
from fastapi import UploadFile
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
os.environ["API_KEY"] = "sk_track2_987654321"

from src.routes.analyze import analyze_document

async def main():
    print("Testing analyze_document() API mapped for automated tests...")
    
    # Create an UploadFile mock as if it was sent via HTTP form-data
    with open("test_doc.docx", "rb") as f:
        data = f.read()
        
    mock_file = UploadFile(
        filename="test_doc.docx",
        file=io.BytesIO(data),
        headers={"content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    )
    
    auth_header = "Bearer sk_track2_987654321"
    
    try:
        # Pass the mock file dependency exactly as the router expects
        res = await analyze_document(file=mock_file, _=auth_header)
        print("\n--- TESTER RESULTS ---")
        from pprint import pprint
        pprint(res)
    except Exception as e:
        print("ERROR:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
