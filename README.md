# 📄 Application de Facturation avec Signature UOV

Application de facturation avec signature numérique post-quantique utilisant le schéma **UOV (Unbalanced Oil and Vinegar)**.

## 🎓 Projet Académique

**École Nationale Supérieure Polytechnique de Yaoundé**
Science de l'Information - Cryptographie
Année Académique : 2025/2026

### Équipe

- **Kamaya Ndigwa ESPERANCE** (23P662) - Cheffe
- **Kengni Kougoum ALAN TRÈSOR** (25P836)
- **Wafo Wafo MICHEL KERAN** (23P327)
- **Akoa Nkengué AIME THIBAUT** (20P200)
- **Kamte Moafo AMSTRONG** (21P017)
- **Tsafack Djoukeng Miderline Flore** (23P572)

**Superviseur :** Dr. Tale Kalachi

---

## 🔐 Qu'est-ce que UOV ?

Le schéma **UOV (Unbalanced Oil and Vinegar)** est un système de signature numérique basé sur la cryptographie multivariée, conçu pour résister aux attaques quantiques. Il repose sur la difficulté de résoudre des systèmes d'équations quadratiques multivariées, un problème NP-difficile même pour les ordinateurs quantiques.

### Principe de Fonctionnement

- **Variables Oil (o)** : Ne peuvent pas se multiplier entre elles
- **Variables Vinegar (v)** : Peuvent se multiplier entre elles et avec Oil
- **Déséquilibre** : v > o (d'où "Unbalanced")

### Paramètres de cette Implémentation

- Corps fini : **GF(31)**
- Variables Oil (o) : **5**
- Variables Vinegar (v) : **10**
- Total variables (n) : **15**

---

## 🏗️ Architecture

```
UOV/
├── backend/              # API FastAPI
│   ├── app.py           # Application principale
│   ├── models.py        # Modèles SQLAlchemy
│   ├── database.py      # Configuration BDD
│   ├── uov_service.py   # Service de signature UOV
│   └── requirements.txt # Dépendances Python
│
├── frontend/            # Interface web
│   ├── index.html       # Page principale
│   ├── styles.css       # Styles CSS
│   └── app.js          # Logique JavaScript
│
├── data/               # Base de données SQLite
│   └── billing.db      # Généré automatiquement
│
└── README.md
```

---

## 🚀 Installation et Démarrage

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Un navigateur web moderne

### Étape 1 : Cloner le Projet

```bash
git clone <url-du-repo>
cd UOV
```

### Étape 2 : Mettre à Jour pip (Recommandé)

```bash
# Windows
python -m pip install --upgrade pip

# Linux/macOS
python3 -m pip install --upgrade pip
```

### Étape 3 : Installer les Dépendances

```bash
cd backend
pip install -r requirements.txt
```

### Étape 4 : Lancer le Serveur Backend

```bash
python app.py
```

Le serveur démarre sur **http://localhost:8000**

Vous devriez voir :
```
✅ Base de données initialisée
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Étape 5 : Ouvrir l'Interface Frontend

Ouvrez le fichier `frontend/index.html` dans votre navigateur :

```bash
# Depuis la racine du projet
cd frontend
# Ouvrir index.html dans votre navigateur
# Ou utiliser un serveur HTTP simple :
python -m http.server 8080
# Puis ouvrir http://localhost:8080
```

---

## 📖 Guide d'Utilisation

### 1. Créer un Client

1. Aller dans l'onglet **"Clients"**
2. Cliquer sur **"+ Nouveau Client"**
3. Remplir les informations :
   - Nom (obligatoire)
   - Email (obligatoire)
   - Adresse (optionnel)
   - Téléphone (optionnel)
4. Cliquer sur **"Créer"**

### 2. Créer une Facture

1. Aller dans l'onglet **"Factures"**
2. Cliquer sur **"+ Nouvelle Facture"**
3. Remplir les informations :
   - Sélectionner un client
   - Description de la facture
   - Ajouter des articles (description, quantité, prix)
4. Cliquer sur **"Créer"**

Une facture est automatiquement créée avec :
- Un numéro unique (FACT-YYYY-XXXXX)
- Une paire de clés UOV (publique/privée)
- Le montant total calculé

### 3. Signer une Facture avec UOV

1. Dans la liste des factures, cliquer sur **"Signer"** pour une facture non signée
2. Confirmer la signature
3. La facture est signée avec le schéma UOV

**Processus de signature :**
1. Le message (données de la facture) est haché avec SHA-256
2. Les variables Vinegar sont choisies aléatoirement
3. Les variables Oil sont calculées
4. La transformation T⁻¹ est appliquée pour obtenir la signature

### 4. Vérifier une Signature

1. Pour une facture signée, cliquer sur **"Vérifier"**
2. Le système vérifie que P(s) = hash(message)
3. Un message de confirmation s'affiche

### 5. Voir les Détails d'une Facture

1. Cliquer sur **"Voir"** dans la liste des factures
2. Une fenêtre modale affiche :
   - Informations du client
   - Articles de la facture
   - Montant total
   - Statut de la signature

---

## 🔧 API Documentation

Le backend expose une API REST complète. Documentation interactive disponible sur :

**http://localhost:8000/docs**

### Endpoints Principaux

#### Clients

- `POST /api/clients` - Créer un client
- `GET /api/clients` - Liste des clients
- `GET /api/clients/{id}` - Détails d'un client
- `PUT /api/clients/{id}` - Modifier un client
- `DELETE /api/clients/{id}` - Supprimer un client

#### Factures

- `POST /api/factures` - Créer une facture
- `GET /api/factures` - Liste des factures
- `GET /api/factures/{id}` - Détails d'une facture
- `GET /api/factures/{id}/details` - Détails complets avec client

#### Signature UOV

- `POST /api/signature/sign` - Signer une facture avec UOV
- `POST /api/signature/verify` - Vérifier une signature UOV

#### Statistiques

- `GET /api/stats` - Statistiques globales

---

## 🔬 Implémentation UOV

### Génération des Clés

```python
from uov_service import generate_uov_keys

public_key, private_key = generate_uov_keys()
```

### Signature

```python
from uov_service import sign_message

message = "Facture N°12345..."
signature = sign_message(message, private_key)
```

### Vérification

```python
from uov_service import verify_signature

is_valid = verify_signature(message, signature, public_key)
```

---

## 🛡️ Sécurité

### Résistance aux Attaques

Le schéma UOV résiste à :

- ✅ **Attaques quantiques** - Problème NP-difficile
- ✅ **Attaque de Kipnis et Shamir** - Structure déséquilibrée
- ✅ **Attaque MinRank** - Rang élevé des matrices
- ✅ **Attaque par intersection** - Variables aléatoires
- ✅ **Attaque directe** - Système masqué

### Avantages

- **Post-quantique** : Résiste aux ordinateurs quantiques
- **Signature rapide** : Génération efficace
- **Vérification simple** : Évaluation polynomiale directe

### Limitations (Version Éducative)

⚠️ Cette implémentation est **éducative/démonstrative** :

- Paramètres simplifiés (q=31, o=5, v=10)
- Arithmétique modulaire simplifiée
- Pour production, utiliser des paramètres NIST recommandés

---

## 📊 Base de Données

### Schéma SQLite

**Table : clients**
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    adresse TEXT,
    telephone TEXT,
    date_creation DATETIME
);
```

**Table : factures**
```sql
CREATE TABLE factures (
    id INTEGER PRIMARY KEY,
    client_id INTEGER FOREIGN KEY,
    numero_facture TEXT UNIQUE NOT NULL,
    date_emission DATETIME,
    montant_total REAL,
    description TEXT,
    items TEXT,
    signature_uov BLOB,
    cle_publique BLOB,
    cle_privee BLOB,
    est_signee BOOLEAN,
    date_signature DATETIME,
    date_creation DATETIME
);
```

---

## 🧪 Tests

### Test Manuel

1. Créer 2-3 clients
2. Créer plusieurs factures
3. Signer quelques factures
4. Vérifier les signatures
5. Consulter les statistiques

### Vérification de la Signature

Pour vérifier manuellement qu'une signature est correcte :

1. La signature doit être valide lors de la vérification
2. Modifier les données de la facture invalide la signature
3. La même facture produit des signatures différentes (aléatoire)

---

## 📝 Fonctionnalités

### Gestion des Clients ✅

- Création, lecture, mise à jour, suppression (CRUD)
- Validation des emails
- Liste complète avec recherche

### Gestion des Factures ✅

- Création avec articles multiples
- Numérotation automatique
- Calcul automatique du montant
- Génération automatique des clés UOV

### Signature UOV ✅

- Signature cryptographique post-quantique
- Génération de clés unique par facture
- Stockage de la signature dans la BDD

### Vérification ✅

- Vérification de l'intégrité
- Validation de l'authenticité
- Feedback visuel clair

### Interface Utilisateur ✅

- Design moderne et responsive
- Dashboard avec statistiques
- Navigation par onglets
- Modales pour les détails
- Notifications en temps réel

---

## 🎯 Objectifs Pédagogiques

Cette application démontre :

1. **Cryptographie Post-Quantique** : Implémentation réelle de UOV
2. **Signature Numérique** : Processus hash-and-sign
3. **Sécurité** : Protection contre les attaques quantiques
4. **Architecture Web** : Stack moderne (FastAPI + Vanilla JS)
5. **Base de Données** : Modélisation et persistance

---

## 🔗 Références

- [UOV Official Site](https://www.uovsig.org/)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Unbalanced Oil and Vinegar - Wikipedia](https://en.wikipedia.org/wiki/Unbalanced_oil_and_vinegar_scheme)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 📄 Licence

Projet académique - École Nationale Supérieure Polytechnique de Yaoundé

---

## 👥 Support

Pour toute question ou problème :

- Contacter l'équipe du projet
- Consulter le superviseur : Dr. Tale Kalachi

---

**Bon apprentissage de la cryptographie post-quantique ! 🔐**
