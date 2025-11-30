#!/bin/bash
# Script de démarrage rapide

echo "🚀 Démarrage du Backend UOV Simplifié"
echo "======================================"
echo ""

# Vérifier si les dépendances sont installées
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
    echo ""
fi

echo "✅ Démarrage du serveur..."
python3 app.py
