from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    sources: Optional[List[str]] = []
    timestamp: datetime

class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime
    sources: Optional[List[str]] = []
    
    class Config:
        from_attributes = True