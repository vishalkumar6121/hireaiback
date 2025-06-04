from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import Optional, Dict, Any
from app.models.user import UserCreate, User, LoginRequest
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from supabase import Client
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@router.post("/signup")
async def signup(user: UserCreate) -> Dict[str, Any]:
    try:
        # Check if passwords match
        if user.password != user.confirmPassword:
            return {
                "success": False,
                "message": "Passwords do not match"
            }

        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "full_name": user.full_name,
                    "role": user.role
                },
                "email_confirm": False
            }
        })
        
        if auth_response.user:
            return {
                "success": True,
                "message": "User registered successfully",
                "token": auth_response.session.access_token,
                "token_type": "bearer",
                "user": {
                    "id": auth_response.user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to create user"
            }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.post("/login")
async def login(credentials: LoginRequest) -> Dict[str, Any]:
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if auth_response.user:
            return {
                "success": True,
                "message": "Login successful",
                "token": auth_response.session.access_token,
                "token_type": "bearer",
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "full_name": auth_response.user.user_metadata.get("full_name", ""),
                    "role": auth_response.user.user_metadata.get("role", "")
                }
            }
        else:
            return {
                "success": False,
                "message": "Incorrect email or password"
            }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        # Sign out from Supabase Auth
        supabase.auth.sign_out()
        return {
            "success": True,
            "message": "Successfully logged out"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        } 