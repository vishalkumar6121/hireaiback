from fastapi import APIRouter, Request
from app.models.user_profile import PersonalInfo, Skills, UserProfile
from app.services.user_profile import update_personal_info, update_skills, update_user_profile
from app.services.auth import verify_token

router = APIRouter()

@router.post("/personal-info")
async def update_personal_info_endpoint(
    request: Request,
    personal_info: PersonalInfo
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
        
        # Extract user info from token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return {
                "success": False,
                "data": "Invalid token: missing user ID"
            }
        
        # Update personal info
        return await update_personal_info(user_id, personal_info)
        
    except Exception as e:
        return {
            "success": False,
            "data": f"Failed to update personal information: {str(e)}"
        }

@router.post("/skills")
async def update_skills_endpoint(
    request: Request,
    skills: Skills
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
        
        # Extract user info from token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return {
                "success": False,
                "data": "Invalid token: missing user ID"
            }
        
        # Update skills
        return await update_skills(user_id, skills)
        
    except Exception as e:
        return {
            "success": False,
            "data": f"Failed to update skills: {str(e)}"
        }

@router.post("/profile")
async def update_profile_endpoint(
    request: Request,
    profile: UserProfile
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
        
        # Extract user info from token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return {
                "success": False,
                "data": "Invalid token: missing user ID"
            }
        
        # Update complete profile
        return await update_user_profile(user_id, profile)
        
    except Exception as e:
        return {
            "success": False,
            "data": f"Failed to update profile: {str(e)}"
        } 