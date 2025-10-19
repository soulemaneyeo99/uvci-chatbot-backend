from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import chat, history, documents

# Créer les tables dans la base de données au démarrage (si elles n'existent pas)
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend pour le Chatbot UVCI avec RAG et Gemini AI"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers des différents modules de l'API
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(documents.router)

# Route racine pour vérifier que l'API est en ligne
@app.get("/")
async def root():
    # CORRECTION: L'indentation du dictionnaire a été corrigée
    return {
        "message": f"Bienvenue sur l'API du Chatbot UVCI",
        "version": settings.APP_VERSION,
        "status": "online",
        "endpoints": {
            "chat": "/api/chat",
            "history": "/api/history/conversations",
            "documents": "/api/documents",
            "docs": "/docs"
        }
    }

# Route de "health check" pour la surveillance
@app.get("/health")
async def health_check():
    # CORRECTION: L'indentation du dictionnaire a été corrigée
    return {
        "status": "healthy",
        "gemini_configured": bool(settings.GOOGLE_API_KEY),
        "database": "connected"
    }

# CORRECTION: "name" a été remplacé par "__name__"
# Ce bloc permet de lancer l'application en mode développement avec uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # L'application se rechargera automatiquement après chaque modification
    )
