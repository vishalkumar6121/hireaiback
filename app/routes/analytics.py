from fastapi import APIRouter, Depends
from typing import Dict, Any
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

@router.get("/")
async def get_analytics(token: str = Depends(verify_token)) -> Dict[str, Any]:
    # Get total candidates
    candidates = supabase.table("candidates").select("id").execute()
    total_candidates = len(candidates.data)
    
    # Get candidates by status
    status_counts = {}
    for candidate in candidates.data:
        status = candidate.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Get outreach statistics
    outreach = supabase.table("outreach_messages").select("*").execute()
    total_outreach = len(outreach.data)
    successful_outreach = len([m for m in outreach.data if m.get("status") == "sent"])
    
    # Get top skills
    skills_count = {}
    for candidate in candidates.data:
        for skill in candidate.get("skills", []):
            skills_count[skill] = skills_count.get(skill, 0) + 1
    
    top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_candidates": total_candidates,
        "status_distribution": status_counts,
        "outreach_stats": {
            "total": total_outreach,
            "successful": successful_outreach,
            "success_rate": (successful_outreach / total_outreach * 100) if total_outreach > 0 else 0
        },
        "top_skills": dict(top_skills)
    } 