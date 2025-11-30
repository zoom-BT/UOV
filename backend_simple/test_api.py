"""
Script de test pour l'API UOV simplifiée
Teste tous les endpoints principaux
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"


def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_api():
    """Teste l'API complète"""

    # 1. SANTÉ DE L'API
    print_section("1. Vérification de l'API")
    r = requests.get(f"{BASE_URL}/health")
    print(f"✅ Status: {r.json()}")

    # 2. CRÉER UN CLIENT
    print_section("2. Création d'un client")
    client_data = {
        "nom": "Jean Dupont",
        "email": "jean.dupont@example.com",
        "telephone": "+237 600 11 22 33"
    }
    r = requests.post(f"{BASE_URL}/clients", json=client_data)
    client_id = r.json()['id']
    print(f"✅ Client créé avec ID: {client_id}")

    # 3. LISTER LES CLIENTS
    print_section("3. Liste des clients")
    r = requests.get(f"{BASE_URL}/clients")
    print(f"✅ Nombre de clients: {len(r.json())}")
    for client in r.json():
        print(f"   - {client['nom']} ({client['email']})")

    # 4. CRÉER UNE FACTURE
    print_section("4. Création d'une facture (génère clés UOV)")
    facture_data = {
        "client_id": client_id,
        "description": "Consultation en cryptographie",
        "items": [
            {"description": "Consultation UOV", "quantite": 2, "prix_unitaire": 50000},
            {"description": "Formation", "quantite": 1, "prix_unitaire": 100000}
        ]
    }
    r = requests.post(f"{BASE_URL}/factures", json=facture_data)
    result = r.json()
    facture_id = result['id']
    print(f"✅ Facture créée:")
    print(f"   - Numéro: {result['numero']}")
    print(f"   - Montant: {result['montant']:.2f} FCFA")
    print(f"   - Message: {result['message']}")

    # 5. LISTER LES FACTURES
    print_section("5. Liste des factures")
    r = requests.get(f"{BASE_URL}/factures")
    print(f"✅ Nombre de factures: {len(r.json())}")
    for facture in r.json():
        status = "✅ Signée" if facture['est_signee'] else "❌ Non signée"
        print(f"   - {facture['numero']} - {facture['client_nom']} - {status}")

    # 6. SIGNER AVEC UOV
    print_section("6. Signature UOV de la facture")
    r = requests.post(f"{BASE_URL}/signature/signer", json={"facture_id": facture_id})
    result = r.json()
    print(f"✅ {result['message']}")
    print(f"   - Signature (extrait): {result['signature'][:100]}...")

    # 7. VÉRIFIER LA SIGNATURE
    print_section("7. Vérification de la signature UOV")
    r = requests.post(f"{BASE_URL}/signature/verifier", json={"facture_id": facture_id})
    result = r.json()
    print(f"✅ {result['message']}")
    print(f"   - Facture: {result['numero']}")
    print(f"   - Valide: {result['valide']}")

    # 8. DÉMONSTRATION UOV
    print_section("8. Démonstration UOV pure")
    r = requests.post(f"{BASE_URL}/demo/uov", json={"message": "Test signature UOV"})
    result = r.json()
    print(f"✅ Message: {result['message']}")
    print(f"   - Clé publique: {result['cle_publique_taille']} bytes")
    print(f"   - Vérification: {result['verification']}")
    print(f"   - Paramètres: GF({result['parametres']['q']}), " +
          f"Oil={result['parametres']['oil']}, " +
          f"Vinegar={result['parametres']['vinegar']}")

    # 9. STATISTIQUES
    print_section("9. Statistiques globales")
    r = requests.get(f"{BASE_URL}/stats")
    stats = r.json()
    print(f"✅ Statistiques:")
    print(f"   - Clients: {stats['clients']}")
    print(f"   - Factures: {stats['factures']}")
    print(f"   - Factures signées: {stats['factures_signees']}")
    print(f"   - Montant total: {stats['montant_total']:.2f} FCFA")

    print_section("✅ TOUS LES TESTS RÉUSSIS !")


if __name__ == '__main__':
    print("\n🔐 Test de l'API UOV Simplifiée")
    print("⚠️  Assurez-vous que le serveur tourne sur http://localhost:5000\n")

    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter à l'API")
        print("   Lancez d'abord: python app.py")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
