"""
Script pour créer des données de démonstration
"""

import requests
import time

API_URL = "http://localhost:8000/api"


def create_demo_clients():
    """Créer des clients de démonstration"""
    clients = [
        {
            "nom": "Société ABC SARL",
            "email": "contact@abc-sarl.cm",
            "adresse": "Yaoundé, Bastos",
            "telephone": "+237 6 99 99 99 99"
        },
        {
            "nom": "Entreprise XYZ",
            "email": "info@xyz-corp.cm",
            "adresse": "Douala, Akwa",
            "telephone": "+237 6 77 77 77 77"
        },
        {
            "nom": "Boutique Tech Plus",
            "email": "contact@techplus.cm",
            "adresse": "Yaoundé, Ngoa-Ekellé",
            "telephone": "+237 6 55 55 55 55"
        }
    ]

    created_clients = []
    for client in clients:
        try:
            response = requests.post(f"{API_URL}/clients", json=client)
            if response.status_code == 201:
                created_clients.append(response.json())
                print(f"✓ Client créé: {client['nom']}")
            else:
                print(f"✗ Erreur pour {client['nom']}: {response.text}")
        except Exception as e:
            print(f"✗ Erreur de connexion: {e}")

    return created_clients


def create_demo_factures(clients):
    """Créer des factures de démonstration"""
    factures = [
        {
            "client_id": clients[0]['id'],
            "description": "Services de développement web",
            "items": [
                {
                    "description": "Développement site web responsive",
                    "quantite": 1,
                    "prix_unitaire": 500000
                },
                {
                    "description": "Hébergement annuel",
                    "quantite": 1,
                    "prix_unitaire": 50000
                }
            ]
        },
        {
            "client_id": clients[1]['id'],
            "description": "Fourniture de matériel informatique",
            "items": [
                {
                    "description": "Ordinateur portable HP ProBook",
                    "quantite": 3,
                    "prix_unitaire": 350000
                },
                {
                    "description": "Souris sans fil",
                    "quantite": 3,
                    "prix_unitaire": 5000
                },
                {
                    "description": "Clé USB 32GB",
                    "quantite": 5,
                    "prix_unitaire": 3000
                }
            ]
        },
        {
            "client_id": clients[2]['id'],
            "description": "Formation en cryptographie",
            "items": [
                {
                    "description": "Formation UOV et cryptographie post-quantique",
                    "quantite": 2,
                    "prix_unitaire": 150000
                },
                {
                    "description": "Documentation technique",
                    "quantite": 2,
                    "prix_unitaire": 10000
                }
            ]
        }
    ]

    created_factures = []
    for facture in factures:
        try:
            response = requests.post(f"{API_URL}/factures", json=facture)
            if response.status_code == 201:
                created_factures.append(response.json())
                print(f"✓ Facture créée: {response.json()['numero_facture']}")
            else:
                print(f"✗ Erreur: {response.text}")
        except Exception as e:
            print(f"✗ Erreur de connexion: {e}")

    return created_factures


def sign_some_factures(factures):
    """Signer quelques factures pour la démo"""
    # Signer les 2 premières factures
    for i in range(min(2, len(factures))):
        try:
            response = requests.post(
                f"{API_URL}/signature/sign",
                json={"facture_id": factures[i]['id']}
            )
            if response.status_code == 200:
                print(f"✓ Facture signée: {factures[i]['numero_facture']}")
            else:
                print(f"✗ Erreur de signature: {response.text}")
        except Exception as e:
            print(f"✗ Erreur de connexion: {e}")


def verify_signatures(factures):
    """Vérifier les signatures"""
    for facture in factures:
        if facture.get('est_signee', False):
            try:
                response = requests.post(
                    f"{API_URL}/signature/verify",
                    json={"facture_id": facture['id']}
                )
                if response.status_code == 200:
                    result = response.json()
                    status = "✓ Valide" if result['is_valid'] else "✗ Invalide"
                    print(f"{status}: {facture['numero_facture']}")
            except Exception as e:
                print(f"✗ Erreur de vérification: {e}")


def display_stats():
    """Afficher les statistiques"""
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("\n" + "="*50)
            print("STATISTIQUES")
            print("="*50)
            print(f"Clients: {stats['total_clients']}")
            print(f"Factures: {stats['total_factures']}")
            print(f"Factures signées: {stats['factures_signees']}")
            print(f"Factures non signées: {stats['factures_non_signees']}")
            print(f"Montant total: {stats['montant_total']:,.0f} FCFA")
            print(f"Taux de signature: {stats['taux_signature']}%")
            print("="*50)
    except Exception as e:
        print(f"✗ Erreur: {e}")


def main():
    print("\n" + "="*50)
    print("CRÉATION DES DONNÉES DE DÉMONSTRATION")
    print("="*50 + "\n")

    # Vérifier que le serveur est en cours d'exécution
    try:
        requests.get("http://localhost:8000")
    except:
        print("✗ Le serveur n'est pas en cours d'exécution!")
        print("  Lancez d'abord: python app.py")
        return

    print("Étape 1: Création des clients...")
    clients = create_demo_clients()
    time.sleep(0.5)

    if not clients:
        print("✗ Aucun client créé. Arrêt.")
        return

    print("\nÉtape 2: Création des factures...")
    factures = create_demo_factures(clients)
    time.sleep(0.5)

    print("\nÉtape 3: Signature de quelques factures avec UOV...")
    sign_some_factures(factures)
    time.sleep(0.5)

    print("\nÉtape 4: Vérification des signatures...")
    verify_signatures(factures)

    print("\nÉtape 5: Affichage des statistiques...")
    display_stats()

    print("\n✓ Données de démonstration créées avec succès!")
    print("\nVous pouvez maintenant ouvrir l'interface web:")
    print("  frontend/index.html")
    print("\nOu consulter l'API:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    main()
