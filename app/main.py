from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import chat, history
# Documents désactivés pour économiser la RAM
# from app.api import documents

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend pour le Chatbot UVCI avec Gemini AI"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accepter toutes les origines pour l'instant
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(chat.router)
app.include_router(history.router)
# app.include_router(documents.router)  # Désactivé

# Route racine
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API du Chatbot UVCI",
        "version": settings.APP_VERSION,
        "status": "online",
        "endpoints": {
            "chat": "/api/chat",
            "history": "/api/history/conversations",
            "docs": "/docs"
        }
    }

# Route de santé
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(settings.GOOGLE_API_KEY),
        "database": "connected"
    }
