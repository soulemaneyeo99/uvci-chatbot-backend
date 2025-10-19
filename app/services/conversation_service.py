
#### **18. Fichier `app/services/conversation_service.py`**
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from typing import List, Optional
from datetime import datetime
import json

class ConversationService:
    """Service pour gérer les conversations"""
    
    @staticmethod
    def create_conversation(title: str, user_id: Optional[str], db: Session) -> Conversation:
        """Crée une nouvelle conversation"""
        conversation = Conversation(
            title=title,
            user_id=user_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_conversation(conversation_id: str, db: Session) -> Optional[Conversation]:
        """Récupère une conversation par ID"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    @staticmethod
    def get_all_conversations(db: Session, limit: int = 50) -> List[Conversation]:
        """Récupère toutes les conversations"""
        return db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def add_message(
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[str]],
        db: Session
    ) -> Message:
        """Ajoute un message à une conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=json.dumps(sources) if sources else None
        )
        db.add(message)
        
        # Mettre à jour la date de la conversation
        conversation = ConversationService.get_conversation(conversation_id, db)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_conversation_messages(conversation_id: str, db: Session) -> List[Message]:
        """Récupère tous les messages d'une conversation"""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
    
    @staticmethod
    def get_conversation_context(conversation_id: str, db: Session, limit: int = 10) -> List[dict]:
        """
        Récupère le contexte récent d'une conversation pour l'IA
        """
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        # Inverser pour avoir l'ordre chronologique
        messages = reversed(messages)
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    @staticmethod
    def delete_conversation(conversation_id: str, db: Session) -> bool:
        """Supprime une conversation et ses messages"""
        try:
            conversation = ConversationService.get_conversation(conversation_id, db)
            if conversation:
                db.delete(conversation)
                db.commit()
                return True
            return False
        except:
            return False

# Instance globale
conversation_service = ConversationService()

