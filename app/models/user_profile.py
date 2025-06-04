from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional

class PersonalInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: Optional[str] = ""
    summary: Optional[str] = ""

class Skills(BaseModel):
    programming: List[str] = []
    frameworks: List[str] = []
    databases: List[str] = []
    cloud: List[str] = []
    tools: List[str] = []
    ai_ml: List[str] = []
    payment_gateways: List[str] = []

class UserProfile(BaseModel):
    personal_info: PersonalInfo
    skills: Skills 