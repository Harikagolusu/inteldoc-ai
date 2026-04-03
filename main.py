import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from src.routes import analyze

app = FastAPI(
    title="IntelDoc AI Document Analysis API",
    description="AI-powered document analysis web application",
    version="1.0.0"
)

# CORS middleware to allow requests if frontend is served elsewhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(analyze.router)

# Serve static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    # Use environment port for deployment (e.g., Render)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)