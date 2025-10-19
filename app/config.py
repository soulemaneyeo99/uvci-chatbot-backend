from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./uvci_chatbot.db"
    
    # App
    APP_NAME: str = "Chatbot UVCI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = ".pdf"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Gemini
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    
    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 3
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()