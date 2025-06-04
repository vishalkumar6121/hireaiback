from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OutreachTemplateBase(BaseModel):
    name: str
    subject: str
    body: str
    category: str

class OutreachTemplateCreate(OutreachTemplateBase):
    pass

class OutreachTemplate(OutreachTemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OutreachMessage(BaseModel):
    template_id: str
    candidate_id: str
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str = "pending"
    sent_at: Optional[datetime] = None 