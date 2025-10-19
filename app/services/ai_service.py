import google.generativeai as genai
from app.config import settings
from typing import List, Dict, Optional
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de Gemini
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    logger.info("✅ Gemini API configurée avec succès")
except Exception as e:
    logger.error(f"❌ Échec de configuration Gemini API: {e}")
    raise

class GeminiService:
    def __init__(self):
        """Initialise le service Gemini avec les modèles 2.5"""
        try:
            # Liste des modèles Gemini 2.5 à essayer dans l'ordre
            model_candidates = [
                'gemini-2.5-flash',           # Le plus rapide
                'gemini-2.5-flash-lite',      # Version allégée
                'gemini-2.5-pro',             # Le plus puissant
            ]
            
            # Trouver le premier modèle qui fonctionne
            model_name = None
            for candidate in model_candidates:
                try:
                    test_model = genai.GenerativeModel(candidate)
                    # Test rapide
                    test_response = test_model.generate_content(
                        "Test", 
                        generation_config={'max_output_tokens': 5}
                    )
                    model_name = candidate
                    logger.info(f"✅ Modèle sélectionné: {model_name}")
                    break
                except Exception as e:
                    logger.debug(f"❌ Modèle {candidate} non disponible: {str(e)[:50]}")
                    continue
            
            if not model_name:
                # Utiliser le premier modèle disponible de la liste
                model_name = 'gemini-2.5-flash'
                logger.warning(f"⚠️  Utilisation du modèle par défaut: {model_name}")
            
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name
            logger.info(f"🚀 Modèle Gemini initialisé: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation modèle: {e}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système pour le chatbot UVCI"""
        return """Tu es l'assistant virtuel officiel de l'Université Virtuelle de Côte d'Ivoire (UVCI).

🎓 TON RÔLE:
- Aider les étudiants avec des informations précises sur l'UVCI
- Répondre aux questions sur les admissions, programmes, frais, calendrier académique
- Être chaleureux, professionnel et encourageant
- Utiliser les documents fournis comme source principale

📋 RÈGLES:
1. Base-toi UNIQUEMENT sur les documents UVCI fournis
2. Si l'info n'est pas dans les documents, dis-le clairement
3. Sois concis (2-4 phrases sauf si détails demandés)
4. Utilise des emojis appropriés 
5. Propose des questions de suivi pertinentes
6. Pour les questions complexes, suggère de contacter l'administration

🚫 À ÉVITER:
- Inventer des informations
- Donner des conseils financiers/légaux
- Partager des opinions personnelles
- Discuter de sujets hors UVCI"""

    def generate_response(
        self, 
        user_message: str, 
        context: Optional[List[Dict]] = None,
        rag_context: Optional[str] = None
    ) -> str:
        """Génère une réponse avec Gemini"""
        try:
            # Construire le prompt système
            system_prompt = self._build_system_prompt()
            
            # Ajouter le contexte RAG si disponible
            rag_section = ""
            if rag_context:
                rag_section = f"""

📚 DOCUMENTS UVCI PERTINENTS:
---
{rag_context}
---

Utilise ces documents pour répondre à la question de l'étudiant.
"""
            
            # Construire l'historique de conversation
            history_messages = ""
            if context:
                for msg in context[-6:]:  # 6 derniers messages
                    role = "Étudiant" if msg["role"] == "user" else "Assistant"
                    history_messages += f"{role}: {msg['content']}\n"
            
            # Prompt complet
            full_prompt = f"""{system_prompt}

{rag_section}

{history_messages}

Étudiant: {user_message}

Assistant UVCI:"""
            
            # Générer la réponse
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"❌ Erreur Gemini: {str(e)}")
            return "Désolé, je rencontre un problème technique. Veuillez réessayer."
    
    def generate_conversation_title(self, first_message: str) -> str:
        """Génère un titre court pour la conversation"""
        try:
            prompt = f"""Génère un titre court (3-6 mots maximum) pour cette conversation.
Réponds UNIQUEMENT avec le titre, sans guillemets.

Question: {first_message}

Titre:"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=15,
                )
            )
            
            title = response.text.strip().strip('"').strip("'").rstrip('.')
            return title[:100]
            
        except Exception as e:
            logger.warning(f"⚠️  Erreur titre: {e}")
            return first_message[:50] + "..." if len(first_message) > 50 else first_message

# Instance globale
gemini_service = GeminiService()
