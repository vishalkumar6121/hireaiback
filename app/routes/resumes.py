from fastapi import APIRouter, HTTPException, status, UploadFile, File, Request
from app.services.auth import verify_token
from app.services.resume_parser import parse_resume
import logging
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_resume_endpoint(
    request: Request,
    file: UploadFile = File(...)
):
    try:
        # Debug logging
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"File info: {file.filename}, {file.content_type}")
        
        # Get authorization header
        authorization = request.headers.get("Authorization")
        logger.debug(f"Authorization header: {authorization}")
        
        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "success": False,
                "data": "Invalid authorization header. Expected 'Bearer <token>'"
            }
        
        token = authorization.split(" ")[1]
        logger.debug(f"Extracted token: {token[:10]}...")
        
        # Extract user info from token
        payload = verify_token(token)
        user_id = payload.get("sub")
        user_role = payload.get("role")
        logger.debug(f"User ID: {user_id}, Role: {user_role}")
        
        if not user_id:
            return {
                "success": False,
                "data": "Invalid token: missing user ID"
            }
        
        # Validate file type
        allowed_types = [".pdf", ".docx"]
        file_extension = os.path.splitext(file.filename)[1].lower()
        logger.debug(f"File extension: {file_extension}")
        
        if file_extension not in allowed_types:
            return {
                "success": False,
                "data": f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            }
        
        # Read file content
        file_content = await file.read()

        # Parse resume using Groq-powered parser
        result = await parse_resume(file_content, file_extension)

        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "data": f"Failed to process resume: {str(e)}"
        } 