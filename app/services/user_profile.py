from fastapi import HTTPException
from app.models.user_profile import PersonalInfo, Skills, UserProfile
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

async def update_personal_info(user_id: str, personal_info: PersonalInfo) -> dict:
    """Update user's personal information."""
    try:
        # Convert personal info to dict
        personal_info_dict = personal_info.dict()
        
        # Update user record
        result = supabase.table("users")\
            .update(personal_info_dict)\
            .eq("id", user_id)\
            .execute()
            
        if not result.data:
            return {
                "success": False,
                "data": "Failed to update personal information"
            }
            
        return {
            "success": True,
            "data": result.data[0]
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": f"Error updating personal information: {str(e)}"
        }

async def update_skills(user_id: str, skills: Skills) -> dict:
    """Update user's skills."""
    try:
        # Convert skills to dict
        skills_dict = skills.dict()
        
        # Update user record
        result = supabase.table("users")\
            .update({"skills": skills_dict})\
            .eq("id", user_id)\
            .execute()
            
        if not result.data:
            return {
                "success": False,
                "data": "Failed to update skills"
            }
            
        return {
            "success": True,
            "data": result.data[0]
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": f"Error updating skills: {str(e)}"
        }

async def update_user_profile(user_id: str, profile: UserProfile) -> dict:
    """Update user's complete profile (personal info and skills)."""
    try:
        # Convert profile to dict
        profile_dict = profile.dict()
        
        # Update user record
        result = supabase.table("users")\
            .update({
                **profile_dict["personal_info"],
                "skills": profile_dict["skills"]
            })\
            .eq("id", user_id)\
            .execute()
            
        if not result.data:
            return {
                "success": False,
                "data": "Failed to update profile"
            }
            
        return {
            "success": True,
            "data": result.data[0]
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": f"Error updating profile: {str(e)}"
        } 