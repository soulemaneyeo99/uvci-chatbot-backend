import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test de santé de l'API"""
    print("🏥 Test de santé...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_chat():
    """Test de l'endpoint chat"""
    print("💬 Test du chat...")
    
    payload = {
        "message": "Bonjour, peux-tu me présenter l'UVCI ?"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat/",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Conversation ID: {data['conversation_id']}")
        print(f"Réponse: {data['response'][:200]}...")
        return data['conversation_id']
    else:
        print(f"Erreur: {response.text}")
    print()

def test_chat_with_context(conversation_id):
    """Test du chat avec contexte"""
    print("💬 Test du chat avec contexte...")
    
    payload = {
        "message": "Quels sont les programmes disponibles ?",
        "conversation_id": conversation_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat/",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Réponse: {data['response'][:200]}...")
    print()

def test_history(conversation_id):
    """Test de l'historique"""
    print("📜 Test de l'historique...")
    
    response = requests.get(
        f"{BASE_URL}/api/history/conversations/{conversation_id}"
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Titre: {data['title']}")
        print(f"Nombre de messages: {len(data['messages'])}")
    print()

def test_suggestions():
    """Test des suggestions"""
    print("💡 Test des suggestions...")
    
    response = requests.get(f"{BASE_URL}/api/chat/suggestions")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Suggestions:")
        for suggestion in data['suggestions']:
            print(f"  - {suggestion}")
    print()

def test_documents():
    """Test de la liste des documents"""
    print("📄 Test des documents...")
    
    response = requests.get(f"{BASE_URL}/api/documents/")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Nombre de documents: {len(data)}")
        for doc in data[:3]:  # Afficher les 3 premiers
            print(f"  - {doc['original_filename']} ({doc['status']})")
    print()

if __name__ == "__main__":
    print("🚀 TESTS DU BACKEND CHATBOT UVCI\n")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        conv_id = test_chat()
        
        if conv_id:
            test_chat_with_context(conv_id)
            test_history(conv_id)
        
        test_suggestions()
        test_documents()
        
        print("=" * 50)
        print("✅ Tests terminés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {str(e)}")