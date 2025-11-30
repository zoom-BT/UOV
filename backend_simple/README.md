# 🚀 Backend Simplifié - Facturation UOV

Version **ultra-légère** du backend avec focus sur UOV.

## ✨ Caractéristiques

- ✅ **Minimal** : Seulement 2 dépendances (Flask + CORS)
- ✅ **Léger** : ~200 lignes de code au total
- ✅ **Simple** : sqlite3 natif (pas de SQLAlchemy)
- ✅ **Focus UOV** : Implémentation claire et pédagogique
- ✅ **Rapide** : Démarrage en 2 commandes

## 📦 Structure

```
backend_simple/
├── uov_core.py          # Cœur UOV (100 lignes)
├── app.py               # API Flask (200 lignes)
├── requirements.txt     # 2 dépendances
├── README.md
└── facturation.db       # Créé automatiquement
```

## 🚀 Installation Ultra-Rapide

### 1. Installer les dépendances

```bash
cd backend_simple
pip install -r requirements.txt
```

### 2. Lancer le serveur

```bash
python app.py
```

C'est tout ! Le serveur démarre sur **http://localhost:5000**

## 📚 API Endpoints

### Clients
```bash
# Lister les clients
GET http://localhost:5000/api/clients

# Créer un client
POST http://localhost:5000/api/clients
{
    "nom": "Jean Dupont",
    "email": "jean@example.com",
    "telephone": "+237 600 00 00 00"
}
```

### Factures
```bash
# Lister les factures
GET http://localhost:5000/api/factures

# Créer une facture (génère automatiquement les clés UOV)
POST http://localhost:5000/api/factures
{
    "client_id": 1,
    "description": "Consultation",
    "items": [
        {"description": "Service A", "quantite": 2, "prix_unitaire": 50000},
        {"description": "Service B", "quantite": 1, "prix_unitaire": 100000}
    ]
}
```

### Signature UOV
```bash
# Signer une facture avec UOV
POST http://localhost:5000/api/signature/signer
{"facture_id": 1}

# Vérifier une signature
POST http://localhost:5000/api/signature/verifier
{"facture_id": 1}
```

### Démonstration UOV
```bash
# Tester UOV directement
POST http://localhost:5000/api/demo/uov
{"message": "Mon message de test"}
```

### Statistiques
```bash
GET http://localhost:5000/api/stats
```

## 🔬 Tester avec cURL

### Créer un client
```bash
curl -X POST http://localhost:5000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Marie Martin",
    "email": "marie@example.com",
    "telephone": "+237 600 11 22 33"
  }'
```

### Créer une facture
```bash
curl -X POST http://localhost:5000/api/factures \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "description": "Prestation de services",
    "items": [
      {"description": "Consultation", "quantite": 1, "prix_unitaire": 75000}
    ]
  }'
```

### Signer avec UOV
```bash
curl -X POST http://localhost:5000/api/signature/signer \
  -H "Content-Type: application/json" \
  -d '{"facture_id": 1}'
```

### Vérifier la signature
```bash
curl -X POST http://localhost:5000/api/signature/verifier \
  -H "Content-Type: application/json" \
  -d '{"facture_id": 1}'
```

### Démo UOV
```bash
curl -X POST http://localhost:5000/api/demo/uov \
  -H "Content-Type: application/json" \
  -d '{"message": "Test de signature UOV"}'
```

## 🎓 Comment ça marche ?

### 1. **uov_core.py** - Le cœur UOV

Implémentation **ultra-simplifiée** du schéma UOV :
- Génération de clés avec structure Oil-Vinegar
- Signature basée sur résolution d'équations quadratiques
- Vérification par évaluation polynomiale

**Paramètres:**
- Corps fini: GF(31)
- Variables Oil (o): 5
- Variables Vinegar (v): 10
- Total: 15 variables

### 2. **app.py** - L'API Flask

API REST minimaliste avec :
- sqlite3 natif (pas de ORM)
- Routes simples et claires
- Focus sur UOV

### 3. **Base de données**

Structure ultra-simple :
```sql
-- Clients
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    email TEXT UNIQUE,
    telephone TEXT
);

-- Factures (avec clés UOV intégrées)
CREATE TABLE factures (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    numero TEXT UNIQUE,
    montant REAL,
    items TEXT,
    cle_publique TEXT,    -- Clé UOV publique
    cle_privee TEXT,      -- Clé UOV privée
    signature TEXT,       -- Signature UOV
    est_signee INTEGER
);
```

## 📊 Workflow Complet

1. **Créer un client**
2. **Créer une facture** → Génère automatiquement les clés UOV
3. **Signer la facture** → Applique le schéma UOV
4. **Vérifier** → Vérifie l'authenticité avec la clé publique

## 🔍 Comparaison avec le backend original

| Aspect | Backend Original | Backend Simplifié |
|--------|-----------------|-------------------|
| **Dépendances** | 8 packages | 2 packages |
| **ORM** | SQLAlchemy | sqlite3 natif |
| **Framework** | FastAPI | Flask |
| **Lignes de code** | ~500 | ~200 |
| **Complexité** | Moyenne | Faible |
| **Focus** | Complet | UOV |

## 💡 Avantages

1. **Facilité d'installation** - 2 packages seulement
2. **Compréhension** - Code clair et minimal
3. **Performance** - Léger et rapide
4. **Pédagogique** - Parfait pour apprendre UOV
5. **Déploiement** - Simple et rapide

## ⚠️ Note

Cette version est **pédagogique et démonstrative**. Pour la production :
- Utiliser des paramètres UOV plus robustes
- Ajouter l'authentification
- Sécuriser les endpoints
- Utiliser HTTPS

## 📚 Références

- [UOV Official](https://www.uovsig.org/)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)

---

**École Nationale Supérieure Polytechnique de Yaoundé**
Superviseur: Dr. Tale Kalachi
