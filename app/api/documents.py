#### **21. Fichier `app/api/documents.py`**
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.document import DocumentUploadResponse, DocumentSchema
from app.services.document_service import document_service
from app.config import settings
from typing import List
import os

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload et index un document PDF
    """
    # Vérifier l'extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS.split(","):
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non autorisé. Autorisés: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Vérifier la taille (fait par FastAPI automatiquement si configuré)
    try:
        # Sauvegarder le fichier
        document = document_service.save_uploaded_file(file, db)
        
        # Lancer l'indexation en arrière-plan
        background_tasks.add_task(document_service.index_document, document, db)
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            upload_date=document.upload_date,
            status=document.status,
            file_size=document.file_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

@router.get("/", response_model=List[DocumentSchema])
async def get_documents(db: Session = Depends(get_db)):
    """Récupère la liste de tous les documents"""
    documents = document_service.get_all_documents(db)
    return documents

@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Récupère un document spécifique"""
    document = document_service.get_document_by_id(document_id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    return document

@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Supprime un document"""
    success = document_service.delete_document(document_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    return {"message": "Document supprimé avec succès"}

@router.post("/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ré-indexe un document"""
    document = document_service.get_document_by_id(document_id, db)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    document.status = "processing"
    db.commit()
    
    background_tasks.add_task(document_service.index_document, document, db)
    
    return {"message": "Ré-indexation lancée"}


