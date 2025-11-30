"""
UOV (Unbalanced Oil and Vinegar) - Implémentation Minimale
Version simplifiée pour démonstration pédagogique
"""

import hashlib
import json
import secrets
from typing import Tuple, List


class UOVSignature:
    """
    Schéma de signature UOV simplifié

    Paramètres:
    - q = 31 (corps fini GF(31))
    - o = 5 (variables Oil)
    - v = 10 (variables Vinegar)
    """

    def __init__(self, q=31, o=5, v=10):
        self.q = q
        self.o = o
        self.v = v
        self.n = o + v

        if v <= o:
            raise ValueError("UOV nécessite v > o")

    def generer_cles(self) -> Tuple[dict, dict]:
        """Génère une paire de clés UOV"""

        # Génération de l'application centrale F
        F = []
        for _ in range(self.o):
            poly = {
                'quad': {},  # Termes quadratiques
                'lin': {},   # Termes linéaires
                'const': secrets.randbelow(self.q)
            }

            # Vinegar-Vinegar (NO Oil-Oil!)
            for i in range(self.v):
                for j in range(i, self.v):
                    c = secrets.randbelow(self.q)
                    if c: poly['quad'][f"{i},{j}"] = c  # Convertir tuple en string

            # Vinegar-Oil
            for i in range(self.v):
                for j in range(self.v, self.n):
                    c = secrets.randbelow(self.q)
                    if c: poly['quad'][f"{i},{j}"] = c  # Convertir tuple en string

            # Linéaires
            for i in range(self.n):
                c = secrets.randbelow(self.q)
                if c: poly['lin'][i] = c

            F.append(poly)

        # Clés
        private_key = {'F': F, 'q': self.q, 'o': self.o, 'v': self.v}
        public_key = {'P': F, 'q': self.q, 'o': self.o, 'v': self.v, 'n': self.n}

        return public_key, private_key

    def signer(self, message: str, private_key: dict) -> str:
        """Signe un message avec UOV"""

        # 1. Hash du message
        h = hashlib.sha256(message.encode()).digest()
        hash_vec = [h[i % len(h)] % self.q for i in range(self.o)]

        # 2. Choisir Vinegar aléatoirement
        vinegar = [secrets.randbelow(self.q) for _ in range(self.v)]

        # 3. Résoudre pour Oil
        oil = []
        for k, poly in enumerate(private_key['F']):
            val = poly['const']

            # Vinegar-Vinegar
            for key, c in poly['quad'].items():
                i, j = map(int, key.split(','))  # Parser la clé string
                if i < self.v and j < self.v:
                    val += c * vinegar[i] * vinegar[j]

            # Linéaires Vinegar
            for i, c in poly['lin'].items():
                if i < self.v:
                    val += c * vinegar[i]

            oil.append((hash_vec[k] - val) % self.q)

        # Signature = Vinegar + Oil
        signature = vinegar + oil

        return json.dumps({
            'sig': signature,
            'q': self.q,
            'o': self.o,
            'v': self.v
        })

    def verifier(self, message: str, signature_json: str, public_key: dict) -> bool:
        """Vérifie une signature UOV"""
        try:
            sig_data = json.loads(signature_json)
            s = sig_data['sig']

            # Hash du message
            h = hashlib.sha256(message.encode()).digest()
            hash_vec = [h[i % len(h)] % self.q for i in range(self.o)]

            # Évaluer P(s)
            result = []
            for poly in public_key['P']:
                val = poly['const']

                # Quadratiques
                for key, c in poly['quad'].items():
                    i, j = map(int, key.split(','))  # Parser la clé string
                    val += c * s[i] * s[j]

                # Linéaires
                for i, c in poly['lin'].items():
                    val += c * s[i]

                result.append(val % self.q)

            return result == hash_vec

        except:
            return False


# Fonctions utilitaires
def generer_cles_uov() -> Tuple[str, str]:
    """Génère et retourne les clés en JSON"""
    uov = UOVSignature()
    pub, priv = uov.generer_cles()
    return json.dumps(pub), json.dumps(priv)


def signer_message(message: str, private_key_json: str) -> str:
    """Signe un message"""
    priv = json.loads(private_key_json)
    uov = UOVSignature(q=priv['q'], o=priv['o'], v=priv['v'])
    return uov.signer(message, priv)


def verifier_signature(message: str, signature: str, public_key_json: str) -> bool:
    """Vérifie une signature"""
    pub = json.loads(public_key_json)
    uov = UOVSignature(q=pub['q'], o=pub['o'], v=pub['v'])
    return uov.verifier(message, signature, pub)
