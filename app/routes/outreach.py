from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.outreach import OutreachTemplate, OutreachTemplateCreate, OutreachMessage
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

@router.get("/templates", response_model=List[OutreachTemplate])
async def get_templates(token: str = Depends(verify_token)):
    result = supabase.table("outreach_templates").select("*").execute()
    return result.data

@router.post("/send")
async def send_outreach(
    message: OutreachMessage,
    token: str = Depends(verify_token)
):
    # Get template
    template = supabase.table("outreach_templates")\
        .select("*")\
        .eq("id", message.template_id)\
        .execute()
    
    if not template.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Get candidate
    candidate = supabase.table("candidates")\
        .select("*")\
        .eq("id", message.candidate_id)\
        .execute()
    
    if not candidate.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Create outreach message
    message_data = message.dict()
    message_data["template"] = template.data[0]
    message_data["candidate"] = candidate.data[0]
    
    result = supabase.table("outreach_messages").insert(message_data).execute()
    return result.data[0] 