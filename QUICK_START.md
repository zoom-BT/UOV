# 🚀 Démarrage Rapide - Application de Facturation UOV

## Installation en 3 étapes

### 1️⃣ Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2️⃣ Lancer le serveur

```bash
python app.py
```

Le serveur démarre sur **http://localhost:8000**

### 3️⃣ Ouvrir l'interface

Ouvrez `frontend/index.html` dans votre navigateur.

---

## 🎯 Test Rapide avec Données de Démo

Une fois le serveur démarré, dans un nouveau terminal :

```bash
cd backend
pip install requests
python demo_data.py
```

Cela créera automatiquement :
- 3 clients de test
- 3 factures
- 2 factures signées avec UOV

---

## 📝 Première Utilisation

1. **Créer un client**
   - Onglet "Clients" → "+ Nouveau Client"
   - Remplir nom et email (obligatoires)

2. **Créer une facture**
   - Onglet "Factures" → "+ Nouvelle Facture"
   - Sélectionner client, ajouter articles

3. **Signer avec UOV**
   - Cliquer sur "Signer" pour une facture
   - La signature UOV est générée automatiquement

4. **Vérifier la signature**
   - Cliquer sur "Vérifier" pour une facture signée
   - Confirmation de validité

---

## 🔍 Explorer l'API

Documentation interactive : **http://localhost:8000/docs**

Endpoints principaux :
- `GET /api/stats` - Statistiques
- `POST /api/clients` - Créer client
- `POST /api/factures` - Créer facture
- `POST /api/signature/sign` - Signer
- `POST /api/signature/verify` - Vérifier

---

## ⚡ Script de Lancement Rapide

```bash
chmod +x start.sh
./start.sh
```

---

## ❓ Problèmes Courants

**Erreur de connexion API ?**
- Vérifiez que le serveur tourne sur http://localhost:8000
- Vérifiez CORS dans les devtools du navigateur

**Module introuvable ?**
- Réinstallez : `pip install -r requirements.txt`

**Base de données ?**
- Elle se crée automatiquement dans `data/billing.db`
- Pour reset : supprimez `data/billing.db` et relancez le serveur

---

## 📚 En savoir plus

Consultez `README.md` pour la documentation complète.

---

**Bon apprentissage de la cryptographie post-quantique ! 🔐**
