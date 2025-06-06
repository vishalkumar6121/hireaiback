from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from typing import List, Optional, Dict, Any
from app.models.candidate import Candidate, CandidateCreate, CandidateUpdate
from app.services.candidate import create_candidate
from app.services.auth import verify_token
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@router.get("/search", response_model=Dict[str, Any])
async def search_candidates(
    request: Request,
    query: Optional[str] = None,
    skills: Optional[List[str]] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None
):
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")

        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "success": False,
                "data": "Invalid authorization header. Expected 'Bearer <token>'"
            }

        token = authorization.split(" ")[1]

        # Verify token (optional, depending on if search needs user ID)
        # payload = verify_token(token)
        # user_id = payload.get("sub")

        # Build query
        query_builder = supabase.table("candidates").select("*")

        if query:
            query_builder = query_builder.ilike("full_name", f"%{query}%")

        if skills:
            for skill in skills:
                query_builder = query_builder.contains("skills", [skill])

        if location:
            query_builder = query_builder.eq("location", location)

        if min_experience:
            query_builder = query_builder.gte("experience_years", min_experience)

        result = query_builder.execute()

        return {
            "success": True,
            "data": result.data
        }

    except Exception as e:
        return {
            "success": False,
            "data": f"Failed to search candidates: {str(e)}"
        }

@router.get("/leaderboard", response_model=List[Candidate])
async def get_leaderboard(token: str = Depends(verify_token)):
    result = supabase.table("candidates")\
        .select("*")\
        .order("score", desc=True)\
        .limit(10)\
        .execute()
    return result.data

@router.post("/{candidate_id}/background-check")
async def run_background_check(
    candidate_id: str,
    token: str = Depends(verify_token)
):
    # Implement background check logic here
    # This is a placeholder for the actual implementation
    return {"status": "background check initiated", "candidate_id": candidate_id} 

@router.post("/")
async def create_candidate_endpoint(
    request: Request,
    candidate: CandidateCreate
):
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        print("Authorization header:", authorization)
        
        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "success": False,
                "data": "Invalid authorization header. Expected 'Bearer <token>'"
            }
        
        token = authorization.split(" ")[1]
        print("Token:", token[:20] + "...")
        
        # Extract user info from token
        payload = verify_token(token)
        print("Token payload:", payload)
        
        user_id = payload.get("sub")
        print("User ID:", user_id)
        
        if not user_id:
            return {
                "success": False,
                "data": "Invalid token: missing user ID"
            }
        
        # Create candidate with user ID as creator
        result = create_candidate(candidate, user_id)
        print("Create candidate result:", result)
        
        if not result["success"]:
            return {
                "success": False,
                "data": result["error"]
            }
            
        return {
            "success": True,
            "data": result["data"]
        }
        
    except Exception as e:
        print("Exception:", str(e))
        return {
            "success": False,
            "data": f"Failed to create candidate: {str(e)}"
        }

@router.get("/{candidate_id}", response_model=Dict[str, Any])
async def get_candidate_details(
    candidate_id: str,
    request: Request
):
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")

        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "success": False,
                "data": "Invalid authorization header. Expected 'Bearer <token>'"
            }

        token = authorization.split(" ")[1]

        # Optional: Verify token if needed for RLS or user-specific logic
        # payload = verify_token(token)
        # user_id = payload.get("sub")

        # Fetch candidate from Supabase
        result = supabase.table("candidates")\
            .select("*")\
            .eq("id", candidate_id)\
            .single()\
            .execute()

        if not result.data:
            return {
                "success": False,
                "data": "Candidate not found"
            }

        return {
            "success": True,
            "data": result.data
        }

    except Exception as e:
        # Check for Supabase-specific errors like not found
        if "PGRST" in str(e): # Supabase specific error indicator
            return {
                "success": False,
                "data": "Candidate not found or database error" # Or more specific error from e
            }
        return {
            "success": False,
            "data": f"Failed to fetch candidate details: {str(e)}"
        }