from fastapi import HTTPException
from app.models.candidate import CandidateCreate
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def create_candidate(candidate_data: CandidateCreate, user_id: str) -> dict:
    """Create a new candidate record."""
    try:
        # Convert candidate data to dict
        candidate_dict = candidate_data.dict()
        
        # Add created_by field
        # candidate_dict["created_by"] = user_id
        
        # Insert into candidates table
        result = supabase.table("candidates")\
            .upsert(candidate_dict, on_conflict=["email"])\
            .execute()
            
        if not result.data:
            return {
                "success": False,
                "error": "Failed to create candidate"
            }
            
        return {
            "success": True,
            "data": result.data[0]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating candidate: {str(e)}"
        }