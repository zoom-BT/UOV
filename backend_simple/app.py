"""
Backend Simplifié - Application de Facturation avec UOV
Version minimaliste avec Flask + sqlite3 natif
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from uov_core import generer_cles_uov, signer_message, verifier_signature

app = Flask(__name__)
CORS(app)  # Active CORS pour le frontend

DB_PATH = "facturation.db"


# ============== BASE DE DONNÉES ==============

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Table Clients
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telephone TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table Factures
    c.execute('''
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            numero TEXT UNIQUE NOT NULL,
            montant REAL NOT NULL,
            description TEXT,
            items TEXT,
            cle_publique TEXT,
            cle_privee TEXT,
            signature TEXT,
            est_signee INTEGER DEFAULT 0,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")


def get_db():
    """Retourne une connexion à la BDD"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour avoir des dictionnaires
    return conn


# ============== ROUTES API ==============

@app.route('/api/health', methods=['GET'])
def health():
    """Vérification de santé de l'API"""
    return jsonify({"status": "ok", "message": "API UOV active"})


# CLIENTS
@app.route('/api/clients', methods=['GET', 'POST'])
def clients():
    """Liste ou crée des clients"""
    conn = get_db()

    if request.method == 'GET':
        clients = conn.execute('SELECT * FROM clients ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(c) for c in clients])

    if request.method == 'POST':
        data = request.json
        try:
            conn.execute(
                'INSERT INTO clients (nom, email, telephone) VALUES (?, ?, ?)',
                (data['nom'], data['email'], data.get('telephone', ''))
            )
            conn.commit()
            client_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.close()
            return jsonify({"id": client_id, "message": "Client créé"}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"error": "Email déjà existant"}), 400


@app.route('/api/clients/<int:id>', methods=['GET'])
def get_client(id):
    """Récupère un client par ID"""
    conn = get_db()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    conn.close()

    if not client:
        return jsonify({"error": "Client introuvable"}), 404

    return jsonify(dict(client))


# FACTURES
@app.route('/api/factures', methods=['GET', 'POST'])
def factures():
    """Liste ou crée des factures"""
    conn = get_db()

    if request.method == 'GET':
        factures = conn.execute('''
            SELECT f.*, c.nom as client_nom
            FROM factures f
            JOIN clients c ON f.client_id = c.id
            ORDER BY f.id DESC
        ''').fetchall()
        conn.close()
        return jsonify([dict(f) for f in factures])

    if request.method == 'POST':
        data = request.json

        # Vérifier que le client existe
        client = conn.execute('SELECT id FROM clients WHERE id = ?',
                             (data['client_id'],)).fetchone()
        if not client:
            conn.close()
            return jsonify({"error": "Client introuvable"}), 404

        # Générer les clés UOV
        pub_key, priv_key = generer_cles_uov()

        # Calculer montant total
        items = data['items']
        montant = sum(item['quantite'] * item['prix_unitaire'] for item in items)

        # Générer numéro de facture
        year = datetime.now().year
        count = conn.execute('SELECT COUNT(*) FROM factures').fetchone()[0]
        numero = f"FACT-{year}-{count+1:05d}"

        # Insérer la facture
        conn.execute('''
            INSERT INTO factures
            (client_id, numero, montant, description, items, cle_publique, cle_privee)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['client_id'],
            numero,
            montant,
            data.get('description', ''),
            json.dumps(items),
            pub_key,
            priv_key
        ))
        conn.commit()
        facture_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()

        return jsonify({
            "id": facture_id,
            "numero": numero,
            "montant": montant,
            "message": "Facture créée avec clés UOV"
        }), 201


@app.route('/api/factures/<int:id>', methods=['GET'])
def get_facture(id):
    """Récupère une facture par ID"""
    conn = get_db()
    facture = conn.execute('''
        SELECT f.*, c.nom as client_nom, c.email as client_email
        FROM factures f
        JOIN clients c ON f.client_id = c.id
        WHERE f.id = ?
    ''', (id,)).fetchone()
    conn.close()

    if not facture:
        return jsonify({"error": "Facture introuvable"}), 404

    result = dict(facture)
    result['items'] = json.loads(result['items'])
    return jsonify(result)


# SIGNATURE UOV
@app.route('/api/signature/signer', methods=['POST'])
def signer():
    """Signe une facture avec UOV"""
    data = request.json
    facture_id = data['facture_id']

    conn = get_db()
    facture = conn.execute('SELECT * FROM factures WHERE id = ?', (facture_id,)).fetchone()

    if not facture:
        conn.close()
        return jsonify({"error": "Facture introuvable"}), 404

    if facture['est_signee']:
        conn.close()
        return jsonify({"error": "Facture déjà signée"}), 400

    # Créer le message à signer
    message = f"{facture['numero']}|{facture['client_id']}|{facture['montant']}|{facture['items']}"

    # Signer avec UOV
    signature = signer_message(message, facture['cle_privee'])

    # Sauvegarder la signature
    conn.execute(
        'UPDATE factures SET signature = ?, est_signee = 1 WHERE id = ?',
        (signature, facture_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "message": f"Facture {facture['numero']} signée avec UOV",
        "signature": signature
    })


@app.route('/api/signature/verifier', methods=['POST'])
def verifier():
    """Vérifie la signature UOV d'une facture"""
    data = request.json
    facture_id = data['facture_id']

    conn = get_db()
    facture = conn.execute('SELECT * FROM factures WHERE id = ?', (facture_id,)).fetchone()
    conn.close()

    if not facture:
        return jsonify({"error": "Facture introuvable"}), 404

    if not facture['est_signee']:
        return jsonify({"error": "Facture non signée"}), 400

    # Recréer le message
    message = f"{facture['numero']}|{facture['client_id']}|{facture['montant']}|{facture['items']}"

    # Vérifier avec UOV
    est_valide = verifier_signature(message, facture['signature'], facture['cle_publique'])

    return jsonify({
        "valide": est_valide,
        "message": "✅ Signature VALIDE" if est_valide else "❌ Signature INVALIDE",
        "numero": facture['numero']
    })


# STATISTIQUES
@app.route('/api/stats', methods=['GET'])
def stats():
    """Retourne les statistiques globales"""
    conn = get_db()

    nb_clients = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
    nb_factures = conn.execute('SELECT COUNT(*) FROM factures').fetchone()[0]
    nb_signees = conn.execute('SELECT COUNT(*) FROM factures WHERE est_signee = 1').fetchone()[0]
    montant_total = conn.execute('SELECT SUM(montant) FROM factures').fetchone()[0] or 0

    conn.close()

    return jsonify({
        "clients": nb_clients,
        "factures": nb_factures,
        "factures_signees": nb_signees,
        "montant_total": montant_total
    })


# DEMO UOV
@app.route('/api/demo/uov', methods=['POST'])
def demo_uov():
    """Démonstration du schéma UOV"""
    data = request.json
    message = data.get('message', 'Test UOV')

    # Générer les clés
    pub_key, priv_key = generer_cles_uov()

    # Signer
    signature = signer_message(message, priv_key)

    # Vérifier
    est_valide = verifier_signature(message, signature, pub_key)

    return jsonify({
        "message": message,
        "cle_publique_taille": len(pub_key),
        "signature": signature[:200] + "...",
        "verification": "✅ VALIDE" if est_valide else "❌ INVALIDE",
        "parametres": {
            "q": 31,
            "oil": 5,
            "vinegar": 10,
            "total": 15
        }
    })


# Servir l'interface de démonstration
@app.route('/')
def index():
    """Interface de démonstration interactive"""
    return send_from_directory('.', 'demo.html')


if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 Backend UOV Simplifié - Démarrage")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("📚 Documentation: http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
