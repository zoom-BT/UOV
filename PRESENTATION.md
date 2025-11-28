# 🎓 Guide de Présentation - Schéma UOV

## Plan de l'Exposé (30-45 minutes)

---

## 1️⃣ Introduction (5 min)

### Contexte
- **Problème** : Menace quantique sur RSA/ECC (Algorithme de Shor)
- **Solution** : Cryptographie Post-Quantique
- **NIST** : Processus de standardisation
- **UOV** : Candidat Round-2 pour signatures numériques

### Objectif du Projet
Concevoir une application de facturation démonstrative utilisant le schéma de signature UOV pour garantir l'authenticité et l'intégrité des factures.

---

## 2️⃣ Fondamentaux UOV (10 min)

### A. Origine et Évolution

```
1988 : MPKC (Matsumoto-Imai)
  ↓
1995 : Attaque de Patarin
  ↓
1997 : Oil & Vinegar (Patarin)
  ↓
1998 : Attaque par sous-espace invariant
  ↓
1999 : Unbalanced Oil & Vinegar (Patarin & Gourbin)
  ↓
2025 : Candidat NIST Round-2
```

### B. Principe Oil-Vinegar

**Analogie :** Huile et Vinaigre ne se mélangent pas !

```
Variables Vinegar (v=10)
├─ Peuvent se multiplier entre elles     ✓
└─ Peuvent se multiplier avec Oil        ✓

Variables Oil (o=5)
└─ NE peuvent PAS se multiplier entre elles  ✗
```

**Déséquilibre :** v > o (d'où "Unbalanced")

### C. Structure Mathématique

**Polynôme type :**
```
P(x₁,...,x₁₅) = Σ c_ij·x_i·x_j + Σ c_i·x_i + c₀

Avec contrainte Oil-Vinegar :
- x_i·x_j où i,j ∈ Vinegar      ✓
- x_i·x_j où i ∈ Vinegar, j ∈ Oil  ✓
- x_i·x_j où i,j ∈ Oil           ✗ INTERDIT
```

---

## 3️⃣ Démonstration de l'Application (15 min)

### A. Architecture

**Stack Technique :**
```
Frontend: HTML/CSS/JavaScript (Vanilla)
Backend: FastAPI (Python)
Base de données: SQLite
Cryptographie: UOV (Implémentation custom)
```

**Structure :**
```
Application de Facturation
├─ Gestion Clients (CRUD)
├─ Gestion Factures
├─ Signature UOV
└─ Vérification
```

### B. Démonstration Live

#### Étape 1 : Lancer l'Application
```bash
# Terminal 1 : Backend
cd backend
python app.py

# Terminal 2 : Données de démo
python demo_data.py

# Navigateur : Frontend
Ouvrir frontend/index.html
```

#### Étape 2 : Dashboard
Montrer les statistiques en temps réel :
- Nombre de clients
- Nombre de factures
- Factures signées vs non signées
- Montant total

#### Étape 3 : Créer un Client
```
Démonstration :
1. Onglet "Clients"
2. "+ Nouveau Client"
3. Remplir : Nom, Email, Adresse, Téléphone
4. "Créer"
```

#### Étape 4 : Créer une Facture
```
Démonstration :
1. Onglet "Factures"
2. "+ Nouvelle Facture"
3. Sélectionner client
4. Ajouter plusieurs articles
5. "Créer"

→ Génération automatique de clés UOV !
```

#### Étape 5 : Signer avec UOV
```
Démonstration :
1. Cliquer "Signer" sur une facture
2. Confirmer

Processus (montrer le code) :
1. Hash SHA-256 du message
2. Choix aléatoire Vinegar
3. Résolution Oil
4. Application T⁻¹
5. Stockage signature
```

#### Étape 6 : Vérifier la Signature
```
Démonstration :
1. Cliquer "Vérifier" sur facture signée
2. Confirmation "Signature valide ✓"

Processus :
1. Calcul P(s)
2. Comparaison avec hash(message)
```

#### Étape 7 : Voir les Détails
```
Démonstration :
1. "Voir" une facture
2. Modal avec toutes les infos
3. Détails du client
4. Articles détaillés
5. Statut de signature
```

---

## 4️⃣ Analyse Cryptographique (10 min)

### A. Algorithme de Signature

**Diagramme de Flux :**

```
Message m
    ↓
[Hash SHA-256]
    ↓
hash_value ∈ GF(q)^o
    ↓
[Choisir Vinegar aléatoirement]
    ↓
vinegar_vars ∈ GF(q)^v
    ↓
[Résoudre pour Oil]
F(vinegar, oil) = hash_value
    ↓
oil_vars ∈ GF(q)^o
    ↓
U = [vinegar | oil]
    ↓
[Appliquer T⁻¹]
    ↓
s = T⁻¹(U)
    ↓
Signature s ∈ GF(q)^n
```

### B. Algorithme de Vérification

```
Message m, Signature s, Clé publique P
    ↓
[Hash SHA-256]
    ↓
hash_value
    ↓
[Évaluer P(s)]
    ↓
result = P(s)
    ↓
[Comparer]
    ↓
result == hash_value ?
├─ Oui → Signature valide ✓
└─ Non → Signature invalide ✗
```

### C. Exemple Numérique

**Paramètres :** q=7, o=1, v=2, n=3

```
Clé Privée :
F : P₁(x₁,x₂,x₃) = x₁·x₃ + 2x₂·x₃ + 3x₁ + x₂ + 1

T : M = [1 2 2]   c = [1]
        [3 5 2]       [2]
        [6 1 1]       [1]

Message : hash(m) = 4

Signature :
1. Choisir Vinegar : x₁=1, x₂=0
2. Résoudre Oil : x₃=0
3. U = [1,0,0]
4. s = T⁻¹(U) = [3,2,0]

Vérification :
P(3,2,0) = F(T(3,2,0)) = F(1,0,0) = 4 ✓
```

---

## 5️⃣ Sécurité (5 min)

### Niveau de Sécurité

**Problème MQ (Multivariate Quadratic) :**
```
Résoudre :
P₁(x₁,...,x_n) = h₁
P₂(x₁,...,x_n) = h₂
...
P_o(x₁,...,x_n) = h_o

→ Problème NP-difficile
→ Résiste aux attaques quantiques
```

### Attaques et Résistance

| Attaque | Résistance UOV |
|---------|----------------|
| **Quantique** (Shor) | ✅ Résistant |
| **Kipnis-Shamir** | ✅ Déséquilibre v>o |
| **MinRank** | ✅ Rang élevé |
| **Intersection** | ✅ Aléatoire |
| **Directe** | ✅ NP-difficile |

### Comparaison

| Critère | UOV | RSA | ECDSA |
|---------|-----|-----|-------|
| Sécurité Quantique | ✅ | ❌ | ❌ |
| Signature rapide | ✅ | ❌ | ✅ |
| Vérification rapide | ⚠️ | ✅ | ✅ |
| Taille clé publique | ❌ Grande | ✅ | ✅ |
| Taille signature | ⚠️ Moyenne | ✅ | ✅ |

---

## 6️⃣ Code Clé (5 min)

### Service UOV - Signature

```python
def sign(self, message: str, private_key: dict) -> bytes:
    # 1. Hash
    hash_value = hashlib.sha256(message.encode()).digest()
    hash_vector = [hash_value[i] % self.q for i in range(self.o)]

    # 2. Choix Vinegar aléatoire
    vinegar_vars = [secrets.randbelow(self.q) for _ in range(self.v)]

    # 3. Résolution Oil (structure Oil-Vinegar)
    oil_vars = self._solve_oil_variables(
        hash_vector, vinegar_vars,
        private_key['F_coefficients'], self.q
    )

    # 4. Construction U
    U = np.array(vinegar_vars + oil_vars)

    # 5. Application T⁻¹
    s = (private_key['T_inv_matrix'] @ U +
         private_key['T_inv_vector']) % self.q

    return s.tobytes()
```

### API FastAPI - Endpoint Signature

```python
@app.post("/api/signature/sign")
def sign_facture(request: SignatureRequest, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id == request.facture_id).first()

    # Message = données facture
    message_data = {
        "numero_facture": facture.numero_facture,
        "client_id": facture.client_id,
        "montant_total": facture.montant_total,
        # ...
    }
    message = json.dumps(message_data, sort_keys=True)

    # Signature UOV
    signature = sign_message(message, facture.cle_privee)

    # Stockage
    facture.signature_uov = signature
    facture.est_signee = True
    db.commit()

    return {"message": "Facture signée avec succès"}
```

---

## 7️⃣ Conclusion (3 min)

### Réalisations

✅ **Application fonctionnelle** de facturation avec UOV
✅ **Implémentation** complète du schéma de signature
✅ **Interface** moderne et intuitive
✅ **Démonstration** de la cryptographie post-quantique

### Avantages UOV

- **Sécurité quantique** : Résiste aux ordinateurs quantiques
- **Signature efficace** : Génération rapide
- **Mathématiques solides** : Problème NP-difficile

### Perspectives

- **Production** : Paramètres NIST (q, o, v plus grands)
- **Optimisations** : Compression des clés
- **Applications** : Blockchain, IoT, Communications sécurisées

### Message Final

> "UOV représente l'avenir de la signature numérique dans un monde où les ordinateurs quantiques deviennent réalité."

---

## 💡 Conseils de Présentation

### Préparation
- [ ] Tester l'application avant (données de démo)
- [ ] Vérifier que le serveur démarre
- [ ] Préparer des factures exemples
- [ ] Avoir le code source ouvert

### Timing
- Introduction : 5 min
- Théorie UOV : 10 min
- **Démo Live** : 15 min (partie la plus importante !)
- Cryptographie : 10 min
- Conclusion : 5 min

### Astuces
1. **Commencer par la démo** pour captiver l'audience
2. **Montrer le code** pendant la démo
3. **Expliquer** chaque étape clairement
4. **Utiliser** l'exemple numérique du rapport
5. **Interagir** avec l'audience (questions)

### Matériel
- Ordinateur avec :
  - Application installée et fonctionnelle
  - Navigateur ouvert sur frontend
  - Terminal avec serveur lancé
  - Code source accessible
- Projecteur/écran
- Support visuel (slides optionnels)

---

## 📊 Slides Suggérés (Si PowerPoint)

1. **Titre** : UOV - Signature Post-Quantique
2. **Contexte** : Menace quantique
3. **UOV** : Principe Oil-Vinegar
4. **Architecture** : Application
5. **Démo** : Screenshots
6. **Algorithme** : Diagramme
7. **Sécurité** : Tableau comparatif
8. **Conclusion** : Résumé

---

## ❓ Questions Probables

**Q: Pourquoi v > o ?**
R: Le déséquilibre empêche l'attaque de Kipnis-Shamir

**Q: Quelle est la taille des clés ?**
R: Plus grande que RSA, mais compressible

**Q: Pourquoi pas juste RSA ?**
R: RSA sera cassé par Shor sur ordinateur quantique

**Q: UOV est-il standardisé ?**
R: Candidat Round-2 NIST (en cours)

**Q: Performance vs RSA ?**
R: Signature plus rapide, vérification comparable

---

**Bonne présentation ! 🎓**
