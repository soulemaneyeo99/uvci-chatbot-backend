from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.chat import MessageSchema

class ConversationSchema(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True

class ConversationDetailSchema(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema]
    
    class Config:
        from_attributes = True