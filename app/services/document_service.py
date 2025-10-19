
#### **17. Fichier `app/services/document_service.py`**
from sqlalchemy.orm import Session
from app.models.document import Document
from app.services.rag_service import rag_service
from app.config import settings
import os
import shutil
from datetime import datetime
from typing import List
import uuid

class DocumentService:
    """Service pour gérer les documents"""
    
    @staticmethod
    def save_uploaded_file(file, db: Session) -> Document:
        """
        Sauvegarde un fichier uploadé et crée l'entrée DB
        """
        # Générer un nom de fichier unique
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_id}{file_extension}"
        
        # Créer le dossier uploads s'il n'existe pas
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Chemin complet
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Obtenir la taille du fichier
        file_size = os.path.getsize(file_path)
        
        # Créer l'entrée dans la DB
        document = Document(
            id=file_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            status="processing",
            file_size=file_size
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    @staticmethod
    def index_document(document: Document, db: Session) -> bool:
        """
        Index un document dans le système RAG
        """
        try:
            # Indexer avec RAG
            chunk_count = rag_service.index_document(
                document.id,
                document.file_path,
                document.original_filename
            )
            
            if chunk_count > 0:
                # Mettre à jour le statut
                document.status = "indexed"
                document.chunk_count = chunk_count
                db.commit()
                return True
            else:
                document.status = "error"
                db.commit()
                return False
                
        except Exception as e:
            print(f"❌ Erreur indexation document: {str(e)}")
            document.status = "error"
            db.commit()
            return False
    
    @staticmethod
    def get_all_documents(db: Session) -> List[Document]:
        """Récupère tous les documents"""
        return db.query(Document).order_by(Document.upload_date.desc()).all()
    
    @staticmethod
    def get_document_by_id(document_id: str, db: Session) -> Document:
        """Récupère un document par son ID"""
        return db.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def delete_document(document_id: str, db: Session) -> bool:
        """Supprime un document"""
        try:
            document = DocumentService.get_document_by_id(document_id, db)
            
            if not document:
                return False
            
            # Supprimer le fichier physique
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Supprimer les chunks du RAG
            rag_service.delete_document_chunks(document_id)
            
            # Supprimer de la DB
            db.delete(document)
            db.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur suppression document: {str(e)}")
            return False

# Instance globale
document_service = DocumentService()
