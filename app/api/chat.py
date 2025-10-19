from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, MessageSchema
from app.services.ai_service import gemini_service
from app.services.conversation_service import conversation_service
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal pour le chat (version sans RAG)
    """
    try:
        # 1. Gérer la conversation
        if request.conversation_id:
            conversation = conversation_service.get_conversation(request.conversation_id, db)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation non trouvée")
        else:
            # Créer une nouvelle conversation
            title = gemini_service.generate_conversation_title(request.message)
            conversation = conversation_service.create_conversation(
                title=title,
                user_id=request.user_id,
                db=db
            )
        
        # 2. RAG désactivé pour économiser la mémoire
        rag_context = None
        sources = []
        
        # 3. Récupérer l'historique de conversation
        conversation_context = conversation_service.get_conversation_context(
            conversation.id, db, limit=6
        )
        
        # 4. Générer la réponse avec Gemini
        ai_response = gemini_service.generate_response(
            user_message=request.message,
            context=conversation_context,
            rag_context=rag_context
        )
        
        # 5. Sauvegarder le message de l'utilisateur
        user_message = conversation_service.add_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            sources=None,
            db=db
        )
        
        # 6. Sauvegarder la réponse de l'assistant
        assistant_message = conversation_service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            sources=sources,
            db=db
        )
        
        # 7. Retourner la réponse
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            sources=sources,
            timestamp=assistant_message.timestamp
        )
        
    except Exception as e:
        print(f"❌ Erreur dans /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/suggestions")
async def get_suggestions():
    """Retourne des suggestions de questions"""
    suggestions = [
        "Quels sont les programmes offerts à l'UVCI ?",
        "Comment s'inscrire à l'UVCI ?",
        "Quels sont les frais de scolarité ?",
        "Quel est le calendrier académique ?",
        "Comment contacter l'administration ?",
        "Quelles sont les conditions d'admission ?",
    ]
    return {"suggestions": suggestions}
