from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from typing import List, Optional, Dict, Any
from app.models.candidate import Candidate, CandidateCreate, CandidateUpdate
from app.services.candidate import create_candidate
from app.services.auth import verify_token
from app.services.nl_search_parser import parse_nl_search_query, SearchCriteria
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# print("Environment variables loaded.")
# print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
# print(f"SUPABASE_KEY (first 5 chars): {os.getenv('SUPABASE_KEY')[:5] if os.getenv('SUPABASE_KEY') else None}")
# print(f"GROQ_API_KEY (first 5 chars): {os.getenv('GROQ_API_KEY')[:5] if os.getenv('GROQ_API_KEY') else None}")

router = APIRouter()
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
# print("Supabase client initialized.")

@router.get("/search", response_model=Dict[str, Any])
async def search_candidates(
    request: Request,
    query: Optional[str] = None,
    skills: Optional[List[str]] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None,
    nl_query: Optional[str] = None # New parameter for natural language query
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

        # --- Natural Language Query Parsing ---
        extracted_criteria = SearchCriteria()
        if nl_query:
            logger.debug(f"Parsing natural language query: {nl_query}")
            logger.debug(f"Calling parse_nl_search_query with nl_query: {nl_query}")
            try:
                parsed_nl = await parse_nl_search_query(nl_query)
                print(f"Parsed NL: {parsed_nl}")
                # Combine extracted criteria from NL query with explicit parameters
                # extracted_criteria.keywords = parsed_nl.keywords
                extracted_criteria.skills = list(set(extracted_criteria.skills + parsed_nl.skills)) # Combine and deduplicate skills
                extracted_criteria.location = parsed_nl.location or location # Prefer NL if provided, else explicit
                extracted_criteria.min_experience_years = parsed_nl.min_experience_years or min_experience # Prefer NL if provided, else explicit
                # Note: 'query' parameter is separate, can be combined with keywords or used for specific name search

            except Exception as nl_parse_error:
                logger.error(f"Failed to parse natural language query: {nl_parse_error}")
                # Continue with only explicit parameters if NL parsing fails
                # Or you might return an error response here depending on desired behavior

        logger.debug(f"Extracted search criteria: {extracted_criteria}")

        # --- Build Supabase Query based *only* on extracted criteria ---
        query_builder = supabase.table("candidates").select("*")

        # Apply filters based on extracted criteria

        # Filter by extracted skills
        if extracted_criteria.skills:
            logger.debug(f"Applying skills filter: contains skills {extracted_criteria.skills}")
            # for skill in extracted_criteria.skills:
            #     # Use .contains works for array columns like 'skills' in Supabase
            #     query_builder = query_builder.contains("skills", [skill])
            query_builder = query_builder.contains("skills", extracted_criteria.skills)

            logger.debug(f"Query builder after skills filter: {query_builder}")

        # Filter by extracted location
        if extracted_criteria.location:
            # Assuming exact location match from parser
            logger.debug(f"Applying location filter: eq location '{extracted_criteria.location}'")
            query_builder = query_builder.eq("location", extracted_criteria.location)
            logger.debug(f"Query builder after location filter: {query_builder}")

        # Filter by extracted minimum experience
        if extracted_criteria.min_experience_years is not None:
            # Convert the float to an integer before using it in the query
            try:
                min_exp_int = int(extracted_criteria.min_experience_years)
                logger.debug(f"Applying min experience filter: gte experience_years {min_exp_int}")
                query_builder = query_builder.gte("experience_years", min_exp_int)
                logger.debug(f"Query builder after experience filter: {query_builder}")
            except (ValueError, TypeError) as e:
                logger.error(f"Could not convert extracted minimum experience {extracted_criteria.min_experience_years} to integer: {e}")
                # Handle cases where the extracted value isn't a valid number
                # For now, just log and skip the filter, but you might raise an error or set a default

        logger.debug("Executing Supabase query...")
        logger.debug(f"Supabase query object: {query_builder}")
        result = query_builder.execute()

        return {
            "success": True,
            "data": result.data
        }

    except Exception as e:
        logger.error(f"Failed to search candidates: {str(e)}")
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
        # print("Authorization header:", authorization)
        
        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "success": False,
                "data": "Invalid authorization header. Expected 'Bearer <token>'"
            }
        
        token = authorization.split(" ")[1]
        # print("Token:", token[:20] + "...")
        
        # Extract user info from token
        payload = verify_token(token)
        # print("Token payload:", payload)
        
        user_id = payload.get("sub")
        # print("User ID:", user_id)
        
        if not user_id:
            return {
                "success": False,
                "data": "Invalid token: missing user ID"
            }
        
        # Create candidate with user ID as creator
        result = create_candidate(candidate, user_id)
        # print("Create candidate result:", result)
        
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
        # print("Exception:", str(e))
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