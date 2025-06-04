from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        # For Supabase JWT tokens, we'll verify by making a request to Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Ensure URL ends with /auth/v1/user
        supabase_url = SUPABASE_URL.rstrip('/')
        auth_url = f"{supabase_url}/auth/v1/user"
        
        print(f"Making request to Supabase URL: {auth_url}")
        print(f"With headers: {headers}")
        
        # Make a request to Supabase to verify the token
        response = requests.get(
            auth_url,
            headers=headers
        )
        
        print(f"Supabase response status: {response.status_code}")
        print(f"Supabase response: {response.text}")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {response.text}",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user data from response
        user_data = response.json()
        print(f"User data: {user_data}")
        
        # Return the token payload
        return {
            "sub": user_data.get("id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "authenticated")
        }
        
    except requests.RequestException as e:
        print(f"Request exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"General exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 