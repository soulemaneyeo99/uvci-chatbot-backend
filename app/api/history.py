#### **20. Fichier `app/api/history.py`**

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.history import ConversationSchema, ConversationDetailSchema
from app.schemas.chat import MessageSchema
from app.services.conversation_service import conversation_service
from typing import List
import json

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(db: Session = Depends(get_db)):
    """Récupère toutes les conversations"""
    conversations = conversation_service.get_all_conversations(db)
    
    return [
        ConversationSchema(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)
        )
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation_detail(conversation_id: str, db: Session = Depends(get_db)):
    """Récupère les détails d'une conversation avec tous ses messages"""
    conversation = conversation_service.get_conversation(conversation_id, db)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    messages = conversation_service.get_conversation_messages(conversation_id, db)
    
    message_schemas = [
        MessageSchema(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp,
            sources=json.loads(msg.sources) if msg.sources else []
        )
        for msg in messages
    ]
    
    return ConversationDetailSchema(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_schemas
    )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Supprime une conversation"""
    success = conversation_service.delete_conversation(conversation_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    return {"message": "Conversation supprimée avec succès"}

