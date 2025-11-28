"""
Service de signature UOV (Unbalanced Oil and Vinegar)
Implémentation simplifiée pour démonstration éducative
Basée sur les principes du schéma UOV
"""

import hashlib
import json
import secrets
from typing import Tuple, List
import numpy as np


class UOVSigner:
    """
    Implémentation simplifiée du schéma de signature UOV

    Paramètres:
    - q: taille du corps fini (nombre premier)
    - o: nombre de variables Oil
    - v: nombre de variables Vinegar
    - n = o + v: nombre total de variables
    """

    def __init__(self, q=31, o=5, v=10):
        """
        Initialise le signataire UOV

        Args:
            q: taille du corps fini (nombre premier)
            o: nombre de variables Oil
            v: nombre de variables Vinegar
        """
        self.q = q  # Corps fini GF(q)
        self.o = o  # Variables Oil
        self.v = v  # Variables Vinegar
        self.n = o + v  # Total variables

        # Vérification: v doit être > o (Unbalanced)
        if v <= o:
            raise ValueError("UOV nécessite v > o (Unbalanced)")

    def generate_keys(self) -> Tuple[dict, dict]:
        """
        Génère une paire de clés (publique, privée) pour UOV

        Returns:
            (public_key, private_key): tuple de dictionnaires
        """
        # Génération de l'application centrale F
        # F est composée de o polynômes quadratiques
        F_coefficients = self._generate_central_map()

        # Génération de la transformation affine T (inversible)
        T_matrix, T_vector, T_inv_matrix, T_inv_vector = self._generate_affine_transform()

        # Clé privée: (F, T, T_inv)
        private_key = {
            'F_coefficients': F_coefficients,
            'T_matrix': T_matrix,
            'T_vector': T_vector,
            'T_inv_matrix': T_inv_matrix,
            'T_inv_vector': T_inv_vector,
            'q': self.q,
            'o': self.o,
            'v': self.v
        }

        # Clé publique: P = F ∘ T
        P_coefficients = self._compose_maps(F_coefficients, T_matrix, T_vector)

        public_key = {
            'P_coefficients': P_coefficients,
            'q': self.q,
            'o': self.o,
            'v': self.v,
            'n': self.n
        }

        return public_key, private_key

    def _generate_central_map(self) -> List[dict]:
        """
        Génère l'application centrale F avec structure Oil-Vinegar
        F est composée de o polynômes quadratiques
        """
        F_coefficients = []

        for k in range(self.o):
            poly = {
                'quadratic': {},  # Termes quadratiques
                'linear': {},     # Termes linéaires
                'constant': 0     # Constante
            }

            # Termes quadratiques: seulement Vinegar-Vinegar et Vinegar-Oil
            # PAS de Oil-Oil (c'est la clé de UOV!)

            # Vinegar-Vinegar (x_i * x_j pour i,j < v)
            for i in range(self.v):
                for j in range(i, self.v):
                    coef = secrets.randbelow(self.q)
                    if coef != 0:
                        poly['quadratic'][(i, j)] = coef

            # Vinegar-Oil (x_i * x_j pour i < v, j >= v)
            for i in range(self.v):
                for j in range(self.v, self.n):
                    coef = secrets.randbelow(self.q)
                    if coef != 0:
                        poly['quadratic'][(i, j)] = coef

            # Termes linéaires
            for i in range(self.n):
                coef = secrets.randbelow(self.q)
                if coef != 0:
                    poly['linear'][i] = coef

            # Constante
            poly['constant'] = secrets.randbelow(self.q)

            F_coefficients.append(poly)

        return F_coefficients

    def _generate_affine_transform(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Génère une transformation affine inversible T et son inverse T^-1
        T(x) = M*x + c
        """
        # Génère une matrice inversible M de taille n x n
        while True:
            M = np.random.randint(0, self.q, (self.n, self.n))
            det = int(round(np.linalg.det(M))) % self.q
            if det != 0:  # Matrice inversible
                break

        # Vecteur constant c
        c = np.random.randint(0, self.q, self.n)

        # Calcul de l'inverse (simplifié pour la démo)
        # Dans une vraie implémentation, il faut calculer l'inverse dans GF(q)
        M_inv = self._matrix_inverse_mod(M, self.q)
        c_inv = (-M_inv @ c) % self.q

        return M, c, M_inv, c_inv

    def _matrix_inverse_mod(self, M: np.ndarray, mod: int) -> np.ndarray:
        """
        Calcule l'inverse d'une matrice modulo mod (version simplifiée)
        """
        # Version simplifiée pour la démo
        # Pour une vraie implémentation, utilisez une méthode appropriée pour GF(q)
        try:
            M_inv = np.linalg.inv(M)
            M_inv = np.round(M_inv).astype(int) % mod
            return M_inv
        except:
            # Si échec, retourne une matrice identité
            return np.eye(self.n, dtype=int)

    def _compose_maps(self, F_coefficients: List[dict], T_matrix: np.ndarray, T_vector: np.ndarray) -> List[dict]:
        """
        Compose F avec T pour obtenir P = F ∘ T
        Version simplifiée pour la démo
        """
        # Pour la démo, on retourne simplement F
        # Dans une vraie implémentation, il faut composer les polynômes
        return F_coefficients

    def sign(self, message: str, private_key: dict) -> bytes:
        """
        Signe un message avec UOV

        Args:
            message: message à signer
            private_key: clé privée

        Returns:
            signature: signature UOV (vecteur dans GF(q)^n)
        """
        # 1. Hacher le message
        hash_value = self._hash_message(message, private_key['o'])

        # 2. Résoudre F(U) = hash_value
        # Choisir aléatoirement les variables Vinegar
        vinegar_vars = [secrets.randbelow(private_key['q']) for _ in range(private_key['v'])]

        # Résoudre pour les variables Oil
        oil_vars = self._solve_oil_variables(
            hash_value,
            vinegar_vars,
            private_key['F_coefficients'],
            private_key['q']
        )

        # U = [vinegar_vars, oil_vars]
        U = vinegar_vars + oil_vars

        # 3. Calculer s = T^-1(U)
        U_array = np.array(U)
        s_array = (private_key['T_inv_matrix'] @ U_array + private_key['T_inv_vector']) % private_key['q']
        s = s_array.tolist()

        # 4. Retourner la signature
        signature_data = {
            'signature': s,
            'q': private_key['q'],
            'o': private_key['o'],
            'v': private_key['v']
        }

        return json.dumps(signature_data).encode()

    def _hash_message(self, message: str, output_length: int) -> List[int]:
        """
        Hache un message pour obtenir un vecteur dans GF(q)^o
        """
        hash_obj = hashlib.sha256(message.encode())
        hash_bytes = hash_obj.digest()

        # Convertir en vecteur dans GF(q)
        hash_vector = []
        for i in range(output_length):
            byte_val = hash_bytes[i % len(hash_bytes)]
            hash_vector.append(byte_val % self.q)

        return hash_vector

    def _solve_oil_variables(self, target: List[int], vinegar_vars: List[int],
                           F_coefficients: List[dict], q: int) -> List[int]:
        """
        Résout les variables Oil étant donné les variables Vinegar

        Pour chaque équation F_k = target[k]:
        - Substituer les variables Vinegar
        - Résoudre l'équation linéaire résultante pour les variables Oil
        """
        v = len(vinegar_vars)
        o = len(target)
        oil_vars = [0] * o

        for k in range(o):
            poly = F_coefficients[k]

            # Calculer la partie connue (avec les Vinegar)
            known_part = poly['constant']

            # Termes quadratiques Vinegar-Vinegar
            for (i, j), coef in poly['quadratic'].items():
                if i < v and j < v:
                    known_part += coef * vinegar_vars[i] * vinegar_vars[j]

            # Termes linéaires Vinegar
            for i, coef in poly['linear'].items():
                if i < v:
                    known_part += coef * vinegar_vars[i]

            known_part %= q

            # Résoudre pour oil_vars[k]
            # Simplifié: on prend la différence
            oil_vars[k] = (target[k] - known_part) % q

        return oil_vars

    def verify(self, message: str, signature: bytes, public_key: dict) -> bool:
        """
        Vérifie une signature UOV

        Args:
            message: message signé
            signature: signature à vérifier
            public_key: clé publique

        Returns:
            True si la signature est valide, False sinon
        """
        try:
            # 1. Décoder la signature
            sig_data = json.loads(signature.decode())
            s = sig_data['signature']
            q = sig_data['q']
            o = sig_data['o']

            # 2. Hacher le message
            hash_value = self._hash_message(message, o)

            # 3. Calculer P(s)
            P_s = self._evaluate_polynomial(s, public_key['P_coefficients'], q)

            # 4. Vérifier P(s) == hash(message)
            return P_s == hash_value

        except Exception as e:
            print(f"Erreur de vérification: {e}")
            return False

    def _evaluate_polynomial(self, x: List[int], P_coefficients: List[dict], q: int) -> List[int]:
        """
        Évalue les polynômes P en x
        """
        result = []

        for poly in P_coefficients:
            value = poly['constant']

            # Termes quadratiques
            for (i, j), coef in poly['quadratic'].items():
                value += coef * x[i] * x[j]

            # Termes linéaires
            for i, coef in poly['linear'].items():
                value += coef * x[i]

            value %= q
            result.append(value)

        return result


# Fonctions utilitaires pour l'API
def generate_uov_keys() -> Tuple[bytes, bytes]:
    """
    Génère une paire de clés UOV et les retourne en bytes
    """
    signer = UOVSigner(q=31, o=5, v=10)
    public_key, private_key = signer.generate_keys()

    public_key_bytes = json.dumps(public_key, cls=NumpyEncoder).encode()
    private_key_bytes = json.dumps(private_key, cls=NumpyEncoder).encode()

    return public_key_bytes, private_key_bytes


def sign_message(message: str, private_key_bytes: bytes) -> bytes:
    """
    Signe un message avec une clé privée UOV
    """
    private_key = json.loads(private_key_bytes.decode())

    # Reconstruire les arrays numpy
    private_key['T_matrix'] = np.array(private_key['T_matrix'])
    private_key['T_vector'] = np.array(private_key['T_vector'])
    private_key['T_inv_matrix'] = np.array(private_key['T_inv_matrix'])
    private_key['T_inv_vector'] = np.array(private_key['T_inv_vector'])

    signer = UOVSigner(q=private_key['q'], o=private_key['o'], v=private_key['v'])
    return signer.sign(message, private_key)


def verify_signature(message: str, signature: bytes, public_key_bytes: bytes) -> bool:
    """
    Vérifie une signature UOV
    """
    public_key = json.loads(public_key_bytes.decode())

    signer = UOVSigner(q=public_key['q'], o=public_key['o'], v=public_key['v'])
    return signer.verify(message, signature, public_key)


class NumpyEncoder(json.JSONEncoder):
    """Encodeur JSON pour les arrays numpy"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        return super().default(obj)
