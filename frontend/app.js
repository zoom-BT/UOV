// Configuration API
const API_URL = 'http://localhost:8000/api';

// État de l'application
let clients = [];
let factures = [];

// ============== INITIALISATION ==============

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadClients();
    loadFactures();

    // Rafraîchir les données toutes les 30 secondes
    setInterval(() => {
        loadStats();
        loadClients();
        loadFactures();
    }, 30000);
});

// ============== NAVIGATION TABS ==============

function showTab(tabName) {
    // Masquer tous les contenus
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Désactiver tous les boutons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Activer le contenu et le bouton sélectionnés
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// ============== STATISTIQUES ==============

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();

        document.getElementById('totalClients').textContent = data.total_clients;
        document.getElementById('totalFactures').textContent = data.total_factures;
        document.getElementById('facturesSignees').textContent = data.factures_signees;
        document.getElementById('montantTotal').textContent = `${data.montant_total.toLocaleString()} FCFA`;
    } catch (error) {
        console.error('Erreur lors du chargement des stats:', error);
    }
}

// ============== GESTION CLIENTS ==============

async function loadClients() {
    try {
        const response = await fetch(`${API_URL}/clients`);
        clients = await response.json();
        displayClients();
        updateClientSelect();
    } catch (error) {
        console.error('Erreur lors du chargement des clients:', error);
        showNotification('Erreur lors du chargement des clients', 'error');
    }
}

function displayClients() {
    const tbody = document.getElementById('clients-list');

    if (clients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="no-data">Aucun client</td></tr>';
        return;
    }

    tbody.innerHTML = clients.map(client => `
        <tr>
            <td>${client.id}</td>
            <td>${client.nom}</td>
            <td>${client.email}</td>
            <td>${client.telephone || '-'}</td>
            <td>
                <button class="btn btn-danger btn-small" onclick="deleteClient(${client.id})">
                    Supprimer
                </button>
            </td>
        </tr>
    `).join('');
}

function updateClientSelect() {
    const select = document.getElementById('factureClient');
    select.innerHTML = '<option value="">Sélectionner un client</option>' +
        clients.map(client => `<option value="${client.id}">${client.nom}</option>`).join('');
}

function showClientForm() {
    document.getElementById('client-form').style.display = 'block';
    document.getElementById('clientNom').focus();
}

function hideClientForm() {
    document.getElementById('client-form').style.display = 'none';
    document.getElementById('clientNom').value = '';
    document.getElementById('clientEmail').value = '';
    document.getElementById('clientAdresse').value = '';
    document.getElementById('clientTelephone').value = '';
}

async function createClient(event) {
    event.preventDefault();

    const clientData = {
        nom: document.getElementById('clientNom').value,
        email: document.getElementById('clientEmail').value,
        adresse: document.getElementById('clientAdresse').value || null,
        telephone: document.getElementById('clientTelephone').value || null
    };

    try {
        const response = await fetch(`${API_URL}/clients`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(clientData)
        });

        if (response.ok) {
            showNotification('Client créé avec succès', 'success');
            hideClientForm();
            loadClients();
            loadStats();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erreur lors de la création', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

async function deleteClient(clientId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce client ?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/clients/${clientId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('Client supprimé avec succès', 'success');
            loadClients();
            loadStats();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

// ============== GESTION FACTURES ==============

async function loadFactures() {
    try {
        const response = await fetch(`${API_URL}/factures`);
        factures = await response.json();
        displayFactures();
    } catch (error) {
        console.error('Erreur lors du chargement des factures:', error);
        showNotification('Erreur lors du chargement des factures', 'error');
    }
}

function displayFactures() {
    const tbody = document.getElementById('factures-list');

    if (factures.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">Aucune facture</td></tr>';
        return;
    }

    tbody.innerHTML = factures.map(facture => {
        const client = clients.find(c => c.id === facture.client_id);
        const clientNom = client ? client.nom : 'Client inconnu';
        const statusBadge = facture.est_signee
            ? '<span class="badge badge-success">✓ Signée</span>'
            : '<span class="badge badge-warning">Non signée</span>';

        return `
            <tr>
                <td>${facture.numero_facture}</td>
                <td>${clientNom}</td>
                <td>${facture.montant_total.toLocaleString()} FCFA</td>
                <td>${new Date(facture.date_emission).toLocaleDateString('fr-FR')}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-primary btn-small" onclick="viewFacture(${facture.id})">
                        Voir
                    </button>
                    ${!facture.est_signee ? `
                        <button class="btn btn-success btn-small" onclick="signFacture(${facture.id})">
                            Signer
                        </button>
                    ` : `
                        <button class="btn btn-secondary btn-small" onclick="verifyFacture(${facture.id})">
                            Vérifier
                        </button>
                    `}
                </td>
            </tr>
        `;
    }).join('');
}

function showFactureForm() {
    if (clients.length === 0) {
        showNotification('Veuillez d\'abord créer un client', 'error');
        return;
    }

    document.getElementById('facture-form').style.display = 'block';
    document.getElementById('factureClient').focus();
}

function hideFactureForm() {
    document.getElementById('facture-form').style.display = 'none';
    document.getElementById('factureClient').value = '';
    document.getElementById('factureDescription').value = '';

    // Reset items
    const itemsContainer = document.getElementById('facture-items');
    itemsContainer.innerHTML = `
        <div class="item-row">
            <input type="text" placeholder="Description" class="item-desc" required>
            <input type="number" placeholder="Qté" class="item-qty" min="1" value="1" required>
            <input type="number" placeholder="Prix unitaire" class="item-price" min="0" step="0.01" required>
            <button type="button" class="btn-remove" onclick="removeItem(this)">×</button>
        </div>
    `;
}

function addItem() {
    const itemsContainer = document.getElementById('facture-items');
    const newItem = document.createElement('div');
    newItem.className = 'item-row';
    newItem.innerHTML = `
        <input type="text" placeholder="Description" class="item-desc" required>
        <input type="number" placeholder="Qté" class="item-qty" min="1" value="1" required>
        <input type="number" placeholder="Prix unitaire" class="item-price" min="0" step="0.01" required>
        <button type="button" class="btn-remove" onclick="removeItem(this)">×</button>
    `;
    itemsContainer.appendChild(newItem);
}

function removeItem(button) {
    const itemsContainer = document.getElementById('facture-items');
    if (itemsContainer.children.length > 1) {
        button.parentElement.remove();
    } else {
        showNotification('Il faut au moins un article', 'error');
    }
}

async function createFacture(event) {
    event.preventDefault();

    // Récupérer les items
    const itemRows = document.querySelectorAll('#facture-items .item-row');
    const items = Array.from(itemRows).map(row => ({
        description: row.querySelector('.item-desc').value,
        quantite: parseInt(row.querySelector('.item-qty').value),
        prix_unitaire: parseFloat(row.querySelector('.item-price').value)
    }));

    const factureData = {
        client_id: parseInt(document.getElementById('factureClient').value),
        description: document.getElementById('factureDescription').value,
        items: items
    };

    try {
        const response = await fetch(`${API_URL}/factures`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(factureData)
        });

        if (response.ok) {
            showNotification('Facture créée avec succès', 'success');
            hideFactureForm();
            loadFactures();
            loadStats();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erreur lors de la création', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

async function viewFacture(factureId) {
    try {
        const response = await fetch(`${API_URL}/factures/${factureId}/details`);
        const data = await response.json();

        const modalBody = document.getElementById('modal-body');
        const items = data.facture.items;

        modalBody.innerHTML = `
            <div class="facture-detail">
                <div class="facture-header">
                    <h2>Facture ${data.facture.numero_facture}</h2>
                    <p>Date: ${new Date(data.facture.date_emission).toLocaleDateString('fr-FR')}</p>
                </div>

                <div class="facture-info">
                    <div>
                        <div class="info-group">
                            <div class="info-label">Client</div>
                            <div class="info-value">${data.client.nom}</div>
                        </div>
                        <div class="info-group">
                            <div class="info-label">Email</div>
                            <div class="info-value">${data.client.email}</div>
                        </div>
                        <div class="info-group">
                            <div class="info-label">Adresse</div>
                            <div class="info-value">${data.client.adresse || '-'}</div>
                        </div>
                    </div>
                    <div>
                        <div class="info-group">
                            <div class="info-label">Téléphone</div>
                            <div class="info-value">${data.client.telephone || '-'}</div>
                        </div>
                        <div class="info-group">
                            <div class="info-label">Description</div>
                            <div class="info-value">${data.facture.description}</div>
                        </div>
                    </div>
                </div>

                <h3>Articles</h3>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Quantité</th>
                            <th>Prix Unitaire</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map(item => `
                            <tr>
                                <td>${item.description}</td>
                                <td>${item.quantite}</td>
                                <td>${item.prix_unitaire.toLocaleString()} FCFA</td>
                                <td>${(item.quantite * item.prix_unitaire).toLocaleString()} FCFA</td>
                            </tr>
                        `).join('')}
                        <tr style="font-weight: bold; background: var(--bg-color);">
                            <td colspan="3">Total</td>
                            <td>${data.facture.montant_total.toLocaleString()} FCFA</td>
                        </tr>
                    </tbody>
                </table>

                <div class="signature-status">
                    ${data.facture.est_signee ? `
                        <h3 style="color: var(--success-color);">✓ Facture signée avec UOV</h3>
                        <p>Date de signature: ${new Date(data.facture.date_signature).toLocaleString('fr-FR')}</p>
                        <button class="btn btn-secondary" onclick="verifyFacture(${data.facture.id}); closeModal();">
                            Vérifier la signature
                        </button>
                    ` : `
                        <h3 style="color: var(--warning-color);">Facture non signée</h3>
                        <button class="btn btn-success" onclick="signFacture(${data.facture.id}); closeModal();">
                            Signer avec UOV
                        </button>
                    `}
                </div>
            </div>
        `;

        document.getElementById('modal-facture').style.display = 'block';
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur lors du chargement des détails', 'error');
    }
}

async function signFacture(factureId) {
    if (!confirm('Voulez-vous signer cette facture avec UOV ?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/signature/sign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ facture_id: factureId })
        });

        if (response.ok) {
            const data = await response.json();
            showNotification(`✓ ${data.message}`, 'success');
            loadFactures();
            loadStats();
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erreur lors de la signature', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

async function verifyFacture(factureId) {
    try {
        const response = await fetch(`${API_URL}/signature/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ facture_id: factureId })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.is_valid) {
                showNotification(`✓ Signature valide pour ${data.numero_facture}`, 'success');
            } else {
                showNotification(`✗ Signature invalide pour ${data.numero_facture}`, 'error');
            }
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erreur lors de la vérification', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

// ============== MODAL ==============

function closeModal() {
    document.getElementById('modal-facture').style.display = 'none';
}

// Fermer la modal en cliquant à l'extérieur
window.onclick = function(event) {
    const modal = document.getElementById('modal-facture');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// ============== NOTIFICATIONS ==============

function showNotification(message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? 'var(--success-color)' : type === 'error' ? 'var(--danger-color)' : 'var(--primary-color)'};
        color: white;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        font-weight: 500;
    `;
    notification.textContent = message;

    // Ajouter au DOM
    document.body.appendChild(notification);

    // Supprimer après 3 secondes
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Ajouter les animations CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
