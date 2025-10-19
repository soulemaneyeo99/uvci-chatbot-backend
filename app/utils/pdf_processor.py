
#### **15. Fichier `app/utils/pdf_processor.py`**
import PyPDF2
import pdfplumber
from typing import List
import re

class PDFProcessor:
    """Classe pour extraire et nettoyer le texte des PDFs"""
    
    @staticmethod
    def extract_text(pdf_path: str, method: str = "pdfplumber") -> str:
        """
        Extrait le texte d'un PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            method: 'pdfplumber' (meilleur) ou 'pypdf2' (fallback)
        """
        try:
            if method == "pdfplumber":
                return PDFProcessor._extract_with_pdfplumber(pdf_path)
            else:
                return PDFProcessor._extract_with_pypdf2(pdf_path)
        except Exception as e:
            print(f"❌ Erreur extraction PDF: {str(e)}")
            # Essayer la méthode alternative
            try:
                alt_method = "pypdf2" if method == "pdfplumber" else "pdfplumber"
                return PDFProcessor.extract_text(pdf_path, alt_method)
            except:
                return ""
    
    @staticmethod
    def _extract_with_pdfplumber(pdf_path: str) -> str:
        """Extraction avec pdfplumber (meilleure qualité)"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text
    
    @staticmethod
    def _extract_with_pypdf2(pdf_path: str) -> str:
        """Extraction avec PyPDF2 (fallback)"""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Nettoie le texte extrait"""
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères spéciaux problématiques
        text = re.sub(r'[^\w\s\-.,;:!?()«»""\'àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]', '', text)
        
        # Normaliser les sauts de ligne
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Découpe le texte en chunks avec overlap
        
        Args:
            text: Texte à découper
            chunk_size: Taille de chaque chunk en caractères
            overlap: Nombre de caractères de chevauchement
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Si ce n'est pas le dernier chunk, trouver la fin du dernier mot
            if end < text_length:
                # Chercher le dernier espace dans les 100 derniers caractères
                last_space = text.rfind(' ', end - 100, end)
                if last_space > start:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < text_length else text_length
        
        return chunks

# Instance globale
pdf_processor = PDFProcessor()
