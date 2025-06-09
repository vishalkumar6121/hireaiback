from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from app.routes import auth, candidates, outreach, analytics, resumes, user_profile
from app.services.auth import verify_token
from app.services.resume import upload_resume

from typing import Dict, Any
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Talent AI Matchmaker API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
app.include_router(user_profile.router, prefix="/api/profile", tags=["profile"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 