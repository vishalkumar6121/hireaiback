from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class CandidateCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    current_position: Optional[str] = None
    desired_position: Optional[str] = None
    status: str = "new"
    resume_url: Optional[str] = None

class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    current_position: Optional[str] = None
    desired_position: Optional[str] = None
    resume_url: Optional[str] = None

class Candidate(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    score: Optional[float] = None
    status: str = "active"

    class Config:
        from_attributes = True 