from sqlalchemy import Column, String, DateTime, Integer
from app.database import Base
from datetime import datetime
import uuid

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="processing")  # processing, indexed, error
    chunk_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Document {self.filename}: {self.status}>"