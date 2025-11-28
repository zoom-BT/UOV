# 🔐 Implémentation du Schéma UOV - Guide Technique

## Vue d'Ensemble

Ce document explique en détail l'implémentation du schéma de signature numérique **UOV (Unbalanced Oil and Vinegar)** dans cette application.

---

## 📊 Paramètres du Système

```python
q = 31    # Taille du corps fini GF(31)
o = 5     # Nombre de variables Oil
v = 10    # Nombre de variables Vinegar
n = 15    # Total de variables (o + v)
```

### Pourquoi ces paramètres ?

- **q = 31** : Un nombre premier pour le corps fini (simplifié pour la démo)
- **v > o** : Condition essentielle du "Unbalanced" (10 > 5)
- En production, des valeurs beaucoup plus grandes seraient utilisées

---

## 🔑 Génération des Clés

### Étape 1 : Application Centrale F

L'application centrale F est composée de **o polynômes quadratiques** avec la structure Oil-Vinegar :

```
Pour chaque polynôme P_k (k = 1 à o) :

P_k(x₁, ..., x_n) = Σ c_ij·x_i·x_j + Σ c_i·x_i + c₀
```

**Structure Oil-Vinegar :**
- ✅ Termes **Vinegar × Vinegar** : `x_i·x_j` où `i,j < v`
- ✅ Termes **Vinegar × Oil** : `x_i·x_j` où `i < v, j ≥ v`
- ❌ **PAS** de termes **Oil × Oil** : `x_i·x_j` où `i,j ≥ v`

C'est cette restriction qui rend le système résolvable avec la trappe !

### Étape 2 : Transformation Affine T

```
T(x) = M·x + c

où :
- M : matrice inversible n×n dans GF(q)
- c : vecteur constant dans GF(q)ⁿ
```

### Étape 3 : Clé Publique P

```
P = F ∘ T

P(x) = F(T(x))
```

La clé publique P masque complètement la structure Oil-Vinegar de F !

### Résumé des Clés

**Clé Privée (Secrète) :**
```json
{
  "F_coefficients": [...],  // Application centrale
  "T_matrix": [...],        // Matrice de transformation
  "T_vector": [...],        // Vecteur de transformation
  "T_inv_matrix": [...],    // Inverse de T
  "T_inv_vector": [...]     // Vecteur inverse
}
```

**Clé Publique :**
```json
{
  "P_coefficients": [...],  // P = F ∘ T
  "q": 31,
  "o": 5,
  "v": 10,
  "n": 15
}
```

---

## ✍️ Processus de Signature

### Entrée
- Message `m` à signer
- Clé privée `(F, T, T⁻¹)`

### Algorithme

#### 1. Hachage du Message

```python
hash_value = SHA256(m) mod GF(q)
→ Vecteur de o éléments dans GF(q)
```

Exemple : `hash_value = [h₁, h₂, h₃, h₄, h₅]` (o=5 éléments)

#### 2. Choix Aléatoire des Variables Vinegar

```python
vinegar_vars = [v₁, v₂, ..., v₁₀]  # 10 valeurs aléatoires dans GF(31)
```

#### 3. Résolution des Variables Oil

Pour chaque équation F_k = h_k :

```
F_k(v₁,...,v₁₀, o₁,...,o₅) = h_k
```

En substituant les variables Vinegar (connues), on obtient une équation linéaire en les variables Oil :

```
Σ c_i·o_i = h_k - (termes Vinegar)
```

On résout pour obtenir : `oil_vars = [o₁, o₂, o₃, o₄, o₅]`

#### 4. Construction de U

```
U = [vinegar_vars || oil_vars]
U = [v₁,...,v₁₀, o₁,...,o₅]  # n = 15 éléments
```

Vérification : `F(U) = hash_value` ✓

#### 5. Application de T⁻¹

```
s = T⁻¹(U)
s = M⁻¹·(U - c)
```

### Sortie

La signature : `s ∈ GF(q)ⁿ` (vecteur de 15 éléments dans GF(31))

Format JSON :
```json
{
  "signature": [s₁, s₂, ..., s₁₅],
  "q": 31,
  "o": 5,
  "v": 10
}
```

---

## ✅ Processus de Vérification

### Entrée
- Message `m`
- Signature `s`
- Clé publique `P`

### Algorithme

#### 1. Hachage du Message

```python
hash_value = SHA256(m) mod GF(q)
```

#### 2. Évaluation de P(s)

```python
result = P(s)
```

On évalue les polynômes de P avec la signature s.

#### 3. Comparaison

```python
if result == hash_value:
    return True  # Signature valide ✓
else:
    return False  # Signature invalide ✗
```

### Pourquoi ça marche ?

```
P(s) = F(T(s))           # Par définition de P
     = F(T(T⁻¹(U)))      # Car s = T⁻¹(U)
     = F(U)              # Car T(T⁻¹(U)) = U
     = hash_value        # Par construction
```

---

## 🔒 Sécurité

### Principe de Sécurité

Sans la clé privée, un attaquant doit résoudre :

```
P(s) = hash_value
```

C'est-à-dire résoudre un **système d'équations quadratiques multivariées**, un problème **NP-difficile** !

### Problème MQ (Multivariate Quadratic)

```
P₁(x₁,...,x₁₅) = h₁
P₂(x₁,...,x₁₅) = h₂
P₃(x₁,...,x₁₅) = h₃
P₄(x₁,...,x₁₅) = h₄
P₅(x₁,...,x₁₅) = h₅
```

Avec 15 inconnues et 5 équations quadratiques → Extrêmement difficile à résoudre !

### Pourquoi la Trappe Fonctionne ?

Avec la clé privée, on connaît :
1. La structure Oil-Vinegar de F (pas de Oil×Oil)
2. La transformation T⁻¹

Donc on peut :
1. Choisir les Vinegar aléatoirement
2. Résoudre linéairement pour Oil (car pas de Oil×Oil !)
3. Appliquer T⁻¹

**Sans la trappe** : Impossible de profiter de la structure Oil-Vinegar (elle est masquée par T) !

---

## 🎯 Exemple Concret

Reprenons l'exemple du rapport avec q=7, o=1, v=2, n=3 :

### Données
```
Corps fini: GF(7) = {0,1,2,3,4,5,6}
Message hash: 4
```

### Génération des Clés

**Application centrale F :**
```
P₁(x₁,x₂,x₃) = x₁·x₃ + 2x₂·x₃ + 3x₁ + x₂ + 1

Structure Oil-Vinegar:
- Vinegar: x₁, x₂ (v=2)
- Oil: x₃ (o=1)
- Termes Vinegar×Oil: x₁·x₃, x₂·x₃ ✓
- Pas de Oil×Oil (x₃·x₃ absent) ✓
```

**Transformation T :**
```
M = [1 2 2]     c = [1]
    [3 5 2]         [2]
    [6 1 1]         [1]

T(x) = M·x + c
```

### Signature (hash = 4)

1. **Choix Vinegar :** x₁=1, x₂=0

2. **Résolution Oil :**
   ```
   P₁(1,0,x₃) = 4
   1·x₃ + 2·0·x₃ + 3·1 + 0 + 1 = 4
   x₃ + 4 = 4  (mod 7)
   x₃ = 0
   ```

3. **U = [1, 0, 0]**

4. **s = T⁻¹(U) = [3, 2, 0]**

### Vérification

```
P(s) = F(T(s))
T(3,2,0) = M·[3,2,0]ᵀ + c = [1,0,0] = U
F(1,0,0) = 1·0 + 2·0·0 + 3·1 + 0 + 1 = 4 ✓
```

La signature est **valide** !

---

## 💻 Code Clé

### Signature
```python
def sign(self, message: str, private_key: dict) -> bytes:
    # 1. Hash
    hash_value = self._hash_message(message, private_key['o'])

    # 2. Choix Vinegar aléatoire
    vinegar_vars = [secrets.randbelow(q) for _ in range(v)]

    # 3. Résolution Oil
    oil_vars = self._solve_oil_variables(
        hash_value, vinegar_vars,
        private_key['F_coefficients'], q
    )

    # 4. Construction U
    U = vinegar_vars + oil_vars

    # 5. s = T⁻¹(U)
    s = (T_inv_matrix @ U + T_inv_vector) % q

    return s
```

### Vérification
```python
def verify(self, message: str, signature: bytes, public_key: dict) -> bool:
    # 1. Hash
    hash_value = self._hash_message(message, o)

    # 2. Évaluation P(s)
    result = self._evaluate_polynomial(signature, public_key['P_coefficients'], q)

    # 3. Comparaison
    return result == hash_value
```

---

## 📈 Comparaison avec RSA

| Aspect | UOV | RSA |
|--------|-----|-----|
| **Base mathématique** | MQ Problem | Factorisation |
| **Sécurité quantique** | ✅ Résistant | ❌ Vulnérable |
| **Taille signature** | Moyenne | Petite |
| **Vitesse signature** | Rapide | Lente |
| **Vitesse vérification** | Moyenne | Rapide |
| **Taille clé publique** | Grande | Petite |

---

## 🎓 Pour l'Exposé

### Points Clés à Présenter

1. **Problème Post-Quantique**
   - Menace de l'algorithme de Shor
   - Besoin de cryptographie résistante

2. **Principe Oil-Vinegar**
   - Structure spéciale des polynômes
   - Déséquilibre v > o

3. **Trappe Secrète**
   - Choix aléatoire Vinegar → résolution linéaire Oil
   - Masquage par transformation affine

4. **Démonstration Live**
   - Créer une facture
   - La signer avec UOV
   - Vérifier la signature
   - Montrer les statistiques

5. **Sécurité**
   - NP-difficulté du problème MQ
   - Résistance aux attaques quantiques

---

## 📚 Ressources

- Rapport : Voir les sections 2 et 3 de votre document
- Code : `backend/uov_service.py`
- Démo : `python demo_data.py`
- Tests : Interface web `frontend/index.html`

---

**Bonne présentation ! 🎯**
