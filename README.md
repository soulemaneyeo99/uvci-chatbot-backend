### 📋 INSTRUCTIONS DE DÉMARRAGE

#### **27. Fichier `README.md`** (backend)
````markdown
# 🎓 Chatbot UVCI - Backend API

Backend FastAPI avec RAG et Gemini AI pour le chatbot intelligent de l'UVCI.

## 🚀 Installation

### 1. Cloner et préparer l'environnement
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration

Créer un fichier `.env` à la racine avec:
```env
GOOGLE_API_KEY=votre_clé_gemini_ici
DATABASE_URL=sqlite:///./uvci_chatbot.db
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Lancer le serveur
```bash
# Mode développement (avec auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou via Python
python app/main.py
```

Le serveur démarre sur: **http://localhost:8000**

Documentation interactive: **http://localhost:8000/docs**

## 🧪 Tests
```bash
# Tester l'API
python test_backend.py
```

## 📁 Structure
````
backend/
├── app/
│   ├── api/          # Endpoints
│   ├── models/       # Modèles DB
│   ├── schemas/      # Validation Pydantic
│   ├── services/     # Logique métier
│   └── utils/        # Utilitaires
├── uploads/          # PDFs uploadés
├── data/            # Base vectorielle
└── requirements.txt