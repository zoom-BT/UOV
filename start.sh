#!/bin/bash

echo "=========================================="
echo "Application de Facturation avec UOV"
echo "=========================================="
echo ""

# Aller dans le dossier backend
cd backend

# Vérifier si les dépendances sont installées
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installation des dépendances..."
    pip install -r requirements.txt
fi

echo ""
echo "Démarrage du serveur FastAPI..."
echo "URL: http://localhost:8000"
echo "Documentation API: http://localhost:8000/docs"
echo ""
echo "Pour ouvrir l'interface:"
echo "  - Ouvrez frontend/index.html dans votre navigateur"
echo "  - Ou lancez: cd frontend && python -m http.server 8080"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Lancer l'application
python app.py
