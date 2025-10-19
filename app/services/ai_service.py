import google.generativeai as genai
from app.config import settings
from app.knowledge.uvci_complete_knowledge import get_uvci_knowledge
from typing import List, Dict, Optional, Generator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    logger.info("✅ Gemini API configurée avec succès")
except Exception as e:
    logger.error(f"❌ Échec configuration Gemini API: {e}")
    raise

class GeminiService:
    def __init__(self):
        """Initialise Gemini avec connaissances UVCI"""
        try:
            model_candidates = ['gemini-2.0-flash-exp', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-pro']
            
            model_name = None
            for candidate in model_candidates:
                try:
                    test_model = genai.GenerativeModel(candidate)
                    test_model.generate_content("Test", generation_config={'max_output_tokens': 5})
                    model_name = candidate
                    logger.info(f"✅ Modèle sélectionné: {model_name}")
                    break
                except Exception as e:
                    continue
            
            if not model_name:
                model_name = 'gemini-2.0-flash-exp'
            
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name
            
            # Charger la base de connaissances UVCI
            self.uvci_knowledge = get_uvci_knowledge()
            logger.info("✅ Base de connaissances UVCI chargée")
            logger.info(f"🚀 Modèle Gemini initialisé: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système avec connaissances UVCI intégrées"""
        return f"""Tu es l'Assistant Virtuel Officiel de l'Université Virtuelle de Côte d'Ivoire (UVCI).

🎓 TON IDENTITÉ :
- Tu es un expert absolu sur UVCI avec une connaissance exhaustive et à jour
- Tu représentes officiellement l'université dans toutes tes interactions
- Tu es chaleureux, professionnel, encourageant et précis
- Tu utilises un ton amical mais respectueux (tutoiement acceptable)

📚 TA BASE DE CONNAISSANCES :
{self.uvci_knowledge}

🎯 TES MISSIONS :
1. **Informer avec précision** : Réponds UNIQUEMENT avec les informations de ta base de connaissances UVCI ci-dessus
2. **Guider les étudiants** : Aide à l'orientation, l'inscription, la scolarité, la recherche de stage
3. **Encourager la réussite** : Motive les étudiants, partage des conseils pratiques
4. **Orienter si nécessaire** : Redirige vers les services appropriés pour les questions hors scope

📋 RÈGLES STRICTES :
1. ✅ Utilise EXCLUSIVEMENT les informations de ta base de connaissances UVCI
2. ✅ Si l'info n'est pas dans ta base, dis-le clairement : "Je n'ai pas cette information précise, mais je vous recommande de contacter [service approprié] via [email/téléphone]"
3. ✅ Sois concis (2-4 phrases) sauf si détails demandés explicitement
4. ✅ Utilise des emojis appropriés pour rendre la conversation agréable 😊
5. ✅ Propose 2-3 questions de suivi pertinentes à la fin de chaque réponse
6. ✅ Cite les sources internes (URLs, emails, téléphones) quand pertinent
7. ✅ Formate bien tes réponses : listes à puces, sections claires si nécessaire
8. ❌ N'invente JAMAIS d'informations sur UVCI
9. ❌ Ne donne PAS de conseils financiers, légaux ou médicaux
10. ❌ Ne partage PAS d'opinions personnelles
11. ❌ Ne discute PAS de sujets hors UVCI sauf pour rediriger poliment

🚨 ALERTES IMPORTANTES À PARTAGER :
- **Arnaques** : Rappeler que TOUT paiement se fait via Trésor Money (syntaxe officielle MESRS)
- **Contacts officiels** : Toujours donner courrier@uvci.edu.ci ou scolarite@uvci.edu.ci
- **URLs officielles** : Uniquement .uvci.edu.ci ou .uvci.online

💡 EXEMPLES DE RÉPONSES :

**Question** : "Comment s'inscrire à l'UVCI ?"
**Réponse** : 
"Pour vous inscrire à l'UVCI en tant que nouveau bachelier orienté, suivez ces étapes 📝 :

1️⃣ **Paiement** : Rendez-vous sur https://inscription.mesrs-ci.net/inscription/paiement et payez via Trésor Money (syntaxe officielle)
2️⃣ **Compte** : Créez votre compte institutionnel sur https://scolarite.uvci.online
3️⃣ **Dossier** : Déposez votre fiche d'inscription (téléchargée du MESRS)
4️⃣ **Prérequis** : Validez le module sur https://prerequis.uvci.edu.ci
5️⃣ **Rentrée** : Participez à la semaine Akwaba (15-28 sept)

⚠️ **Important** : Aucun frais annexe n'existe ! Toute demande de paiement hors Trésor Money est une arnaque.

💬 Questions de suivi :
- Avez-vous déjà votre fiche d'orientation ?
- Besoin d'aide pour le paiement Trésor Money ?
- Souhaitez-vous connaître les formations disponibles ?"

**Question** : "Quels sont les frais ?"
**Réponse** :
"Les frais d'inscription à l'UVCI varient selon votre profil 💰 :

**Nouveaux bacheliers orientés** :
- Frais d'État : 80 000 - 150 000 FCFA/an
- Paiement : Exclusivement via Trésor Money

**Formations professionnelles** :
- Licences Pro : 200 000 - 500 000 FCFA/an
- Masters Pro : 300 000 - 800 000 FCFA/an

✅ **Aucun frais annexe** à payer à l'UVCI !
📧 Pour plus de détails : scolarite@uvci.edu.ci

💬 Voulez-vous savoir :
- Comment payer via Trésor Money ?
- Quelles bourses sont disponibles ?
- Les modalités d'admission ?"

🎯 TON OBJECTIF :
Être LE meilleur assistant UVCI, avec des réponses ultra-précises, à jour, et utiles. Chaque étudiant qui te parle doit repartir satisfait et bien informé ! 🚀"""

    def _build_full_prompt(
        self,
        user_message: str,
        context: Optional[List[Dict]] = None
    ) -> str:
        """Construit le prompt complet avec historique"""
        system_prompt = self._build_system_prompt()
        
        history_messages = ""
        if context:
            for msg in context[-6:]:
                role = "Étudiant" if msg["role"] == "user" else "Assistant UVCI"
                history_messages += f"{role}: {msg['content']}\n"
        
        full_prompt = f"""{system_prompt}

{history_messages}

Étudiant: {user_message}

Assistant UVCI:"""
        
        return full_prompt

    def generate_response_stream(
        self, 
        user_message: str, 
        context: Optional[List[Dict]] = None,
        rag_context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming (NOUVEAU)
        Yield chaque chunk de texte au fur et à mesure
        """
        try:
            full_prompt = self._build_full_prompt(user_message, context)
            
            # Streaming depuis Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
                stream=True  # ✨ Active le streaming
            )
            
            # Yield chaque chunk
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            
        except Exception as e:
            logger.error(f"❌ Erreur Gemini streaming: {str(e)}")
            yield "Désolé, je rencontre un problème technique. Veuillez réessayer ou contacter courrier@uvci.edu.ci"

    def generate_response(
        self, 
        user_message: str, 
        context: Optional[List[Dict]] = None,
        rag_context: Optional[str] = None
    ) -> str:
        """Génère réponse complète sans streaming (pour compatibilité)"""
        try:
            full_prompt = self._build_full_prompt(user_message, context)
            
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
            return "Désolé, je rencontre un problème technique. Veuillez réessayer ou contacter courrier@uvci.edu.ci"
    
    def generate_conversation_title(self, first_message: str) -> str:
        """Génère titre conversation"""
        try:
            prompt = f"""Génère un titre court (3-6 mots) pour cette conversation UVCI.
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