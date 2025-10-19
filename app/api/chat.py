from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import gemini_service
from app.services.conversation_service import conversation_service
import json
import asyncio

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint streaming avec keep-alive pour Render
    """
    async def generate():
        try:
            # 1. Gérer conversation
            if request.conversation_id:
                conversation = conversation_service.get_conversation(
                    request.conversation_id, db
                )
                if not conversation:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Conversation introuvable'})}\n\n"
                    return
            else:
                title = gemini_service.generate_conversation_title(request.message)
                conversation = conversation_service.create_conversation(
                    title=title,
                    user_id=request.user_id,
                    db=db
                )
            
            # Envoyer conversation_id immédiatement
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id})}\n\n"
            await asyncio.sleep(0)
            
            # 2. Contexte
            context = conversation_service.get_conversation_context(
                conversation.id, db, limit=6
            )
            
            # 3. Streaming Gemini avec keep-alive
            full_response = ""
            chunk_count = 0
            
            for chunk in gemini_service.generate_response_stream(
                user_message=request.message,
                context=context
            ):
                full_response += chunk
                chunk_count += 1
                
                # Envoyer le chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # Keep-alive tous les 10 chunks
                if chunk_count % 10 == 0:
                    yield f": keepalive\n\n"
                
                await asyncio.sleep(0)
            
            # 4. Sauvegarder messages
            conversation_service.add_message(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                sources=None,
                db=db
            )
            
            assistant_msg = conversation_service.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response,
                sources=[],
                db=db
            )
            
            # 5. Signal fin
            yield f"data: {json.dumps({
                'type': 'done',
                'message_id': assistant_msg.id,
                'timestamp': assistant_msg.timestamp.isoformat()
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
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint classique sans streaming (fallback)
    """
    try:
        # 1. Conversation
        if request.conversation_id:
            conversation = conversation_service.get_conversation(
                request.conversation_id, db
            )
            if not conversation:
                raise HTTPException(404, "Conversation introuvable")
        else:
            title = gemini_service.generate_conversation_title(request.message)
            conversation = conversation_service.create_conversation(
                title=title,
                user_id=request.user_id,
                db=db
            )
        
        # 2. Contexte
        context = conversation_service.get_conversation_context(
            conversation.id, db, limit=6
        )
        
        # 3. Générer réponse
        ai_response = gemini_service.generate_response(
            user_message=request.message,
            context=context
        )
        
        # 4. Sauvegarder
        conversation_service.add_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            sources=None,
            db=db
        )
        
        assistant_msg = conversation_service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            sources=[],
            db=db
        )
        
        # 5. Retour
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation.id,
            message_id=assistant_msg.id,
            sources=[],
            timestamp=assistant_msg.timestamp
        )
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        raise HTTPException(500, f"Erreur: {str(e)}")

@router.get("/suggestions")
async def get_suggestions():
    """Suggestions de questions"""
    return {"suggestions": [
        "Quels sont les programmes UVCI ?",
        "Comment s'inscrire ?",
        "Quels sont les frais ?",
        "Calendrier académique ?",
        "Contacter l'administration ?",
        "Conditions d'admission ?",
    ]}
