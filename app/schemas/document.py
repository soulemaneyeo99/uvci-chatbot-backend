from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    upload_date: datetime
    status: str
    file_size: int

class DocumentSchema(BaseModel):
    id: str
    filename: str
    original_filename: str
    upload_date: datetime
    status: str
    chunk_count: int
    file_size: int
    
    class Config:
        from_attributes = True