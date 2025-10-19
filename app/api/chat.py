# api/chat.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, MessageSchema
from app.services.ai_service import gemini_service
from app.services.conversation_service import conversation_service
from datetime import datetime
import json
import asyncio

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint avec streaming en temps réel (Server-Sent Events)
    """
    async def generate():
        try:
            # 1. Gérer la conversation
            if request.conversation_id:
                conversation = conversation_service.get_conversation(request.conversation_id, db)
                if not conversation:
                    yield f"data: {json.dumps({'error': 'Conversation non trouvée'})}\n\n"
                    return
            else:
                # Créer une nouvelle conversation
                title = gemini_service.generate_conversation_title(request.message)
                conversation = conversation_service.create_conversation(
                    title=title,
                    user_id=request.user_id,
                    db=db
                )
            
            # Envoyer l'ID de conversation immédiatement
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id})}\n\n"
            
            # 2. Récupérer le contexte
            conversation_context = conversation_service.get_conversation_context(
                conversation.id, db, limit=6
            )
            
            # 3. Générer la réponse avec streaming depuis Gemini
            full_response = ""
            
            # Stream depuis Gemini
            for chunk in gemini_service.generate_response_stream(
                user_message=request.message,
                context=conversation_context,
                rag_context=None
            ):
                full_response += chunk
                # Envoyer chaque chunk au frontend
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Petit délai pour fluidité
            
            # 4. Sauvegarder les messages en DB
            user_message = conversation_service.add_message(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                sources=None,
                db=db
            )
            
            assistant_message = conversation_service.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response,
                sources=[],
                db=db
            )
            
            # 5. Envoyer le signal de fin avec metadata
            yield f"data: {json.dumps({
                'type': 'done',
                'message_id': assistant_message.id,
                'timestamp': assistant_message.timestamp.isoformat()
            })}\n\n"
            
        except Exception as e:
            print(f"❌ Erreur streaming: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Désactive le buffering nginx
        }
    )

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint classique sans streaming (pour compatibilité)
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
        
        # 2. RAG désactivé
        rag_context = None
        sources = []
        
        # 3. Récupérer l'historique de conversation
        conversation_context = conversation_service.get_conversation_context(
            conversation.id, db, limit=6
        )
        
        # 4. Générer la réponse avec Gemini (sans streaming)
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