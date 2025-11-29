"""
Application de facturation avec signature UOV
FastAPI Backend
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import json
from pathlib import Path

from database import get_db, init_db
from models import Client, Facture
from uov_service import generate_uov_keys, sign_message, verify_signature

# Gestionnaire de cycle de vie de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage
    init_db()
    print("✅ Base de données initialisée")
    yield
    # Arrêt (si nécessaire)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Billing App with UOV Signature",
    description="Application de facturation avec signature numérique UOV (Unbalanced Oil and Vinegar)",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== SCHÉMAS PYDANTIC ==============

class ClientCreate(BaseModel):
    nom: str
    email: EmailStr
    adresse: Optional[str] = None
    telephone: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    nom: str
    email: str
    adresse: Optional[str]
    telephone: Optional[str]
    date_creation: datetime

    class Config:
        from_attributes = True


class FactureItem(BaseModel):
    description: str
    quantite: int
    prix_unitaire: float


class FactureCreate(BaseModel):
    client_id: int
    description: str
    items: List[FactureItem]


class FactureResponse(BaseModel):
    id: int
    client_id: int
    numero_facture: str
    date_emission: datetime
    montant_total: float
    description: str
    items: str
    est_signee: bool
    date_signature: Optional[datetime]
    date_creation: datetime

    class Config:
        from_attributes = True


class SignatureRequest(BaseModel):
    facture_id: int


class VerificationRequest(BaseModel):
    facture_id: int


# ============== ENDPOINTS CLIENTS ==============

@app.post("/api/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Créer un nouveau client"""
    # Vérifier si l'email existe déjà
    existing = db.query(Client).filter(Client.email == client.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un client avec cet email existe déjà"
        )

    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@app.get("/api/clients", response_model=List[ClientResponse])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer la liste des clients"""
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients


@app.get("/api/clients/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Récupérer un client par son ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client non trouvé"
        )
    return client


@app.put("/api/clients/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client: ClientCreate, db: Session = Depends(get_db)):
    """Mettre à jour un client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client non trouvé"
        )

    for key, value in client.dict().items():
        setattr(db_client, key, value)

    db.commit()
    db.refresh(db_client)
    return db_client


@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Supprimer un client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client non trouvé"
        )

    # Vérifier s'il a des factures
    if db_client.factures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un client ayant des factures"
        )

    db.delete(db_client)
    db.commit()
    return {"message": "Client supprimé avec succès"}


# ============== ENDPOINTS FACTURES ==============

@app.post("/api/factures", response_model=FactureResponse, status_code=status.HTTP_201_CREATED)
def create_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle facture"""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == facture.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client non trouvé"
        )

    # Calculer le montant total
    montant_total = sum(item.quantite * item.prix_unitaire for item in facture.items)

    # Générer un numéro de facture unique
    facture_count = db.query(Facture).count()
    numero_facture = f"FACT-{datetime.now().year}-{facture_count + 1:05d}"

    # Générer les clés UOV pour cette facture
    public_key, private_key = generate_uov_keys()

    # Créer la facture
    db_facture = Facture(
        client_id=facture.client_id,
        numero_facture=numero_facture,
        montant_total=montant_total,
        description=facture.description,
        items=json.dumps([item.dict() for item in facture.items]),
        cle_publique=public_key,
        cle_privee=private_key,
        est_signee=False
    )

    db.add(db_facture)
    db.commit()
    db.refresh(db_facture)
    return db_facture


@app.get("/api/factures", response_model=List[FactureResponse])
def get_factures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer la liste des factures"""
    factures = db.query(Facture).offset(skip).limit(limit).all()
    return factures


@app.get("/api/factures/{facture_id}", response_model=FactureResponse)
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    """Récupérer une facture par son ID"""
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )
    return facture


@app.get("/api/factures/{facture_id}/details")
def get_facture_details(facture_id: int, db: Session = Depends(get_db)):
    """Récupérer les détails complets d'une facture avec le client"""
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )

    client = db.query(Client).filter(Client.id == facture.client_id).first()

    return {
        "facture": {
            "id": facture.id,
            "numero_facture": facture.numero_facture,
            "date_emission": facture.date_emission,
            "montant_total": facture.montant_total,
            "description": facture.description,
            "items": json.loads(facture.items),
            "est_signee": facture.est_signee,
            "date_signature": facture.date_signature
        },
        "client": {
            "id": client.id,
            "nom": client.nom,
            "email": client.email,
            "adresse": client.adresse,
            "telephone": client.telephone
        }
    }


# ============== ENDPOINTS SIGNATURE UOV ==============

@app.post("/api/signature/sign")
def sign_facture(request: SignatureRequest, db: Session = Depends(get_db)):
    """Signer une facture avec UOV"""
    facture = db.query(Facture).filter(Facture.id == request.facture_id).first()
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )

    if facture.est_signee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette facture est déjà signée"
        )

    # Créer le message à signer (hash de la facture)
    message_data = {
        "numero_facture": facture.numero_facture,
        "client_id": facture.client_id,
        "montant_total": facture.montant_total,
        "description": facture.description,
        "items": facture.items,
        "date_emission": facture.date_emission.isoformat()
    }
    message = json.dumps(message_data, sort_keys=True)

    # Signer avec UOV
    try:
        signature = sign_message(message, facture.cle_privee)

        # Mettre à jour la facture
        facture.signature_uov = signature
        facture.est_signee = True
        facture.date_signature = datetime.utcnow()

        db.commit()

        return {
            "message": "Facture signée avec succès",
            "facture_id": facture.id,
            "numero_facture": facture.numero_facture,
            "date_signature": facture.date_signature,
            "signature_size": len(signature)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la signature: {str(e)}"
        )


@app.post("/api/signature/verify")
def verify_facture(request: VerificationRequest, db: Session = Depends(get_db)):
    """Vérifier la signature UOV d'une facture"""
    facture = db.query(Facture).filter(Facture.id == request.facture_id).first()
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )

    if not facture.est_signee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette facture n'est pas signée"
        )

    # Recréer le message
    message_data = {
        "numero_facture": facture.numero_facture,
        "client_id": facture.client_id,
        "montant_total": facture.montant_total,
        "description": facture.description,
        "items": facture.items,
        "date_emission": facture.date_emission.isoformat()
    }
    message = json.dumps(message_data, sort_keys=True)

    # Vérifier la signature
    try:
        is_valid = verify_signature(message, facture.signature_uov, facture.cle_publique)

        return {
            "facture_id": facture.id,
            "numero_facture": facture.numero_facture,
            "is_valid": is_valid,
            "date_signature": facture.date_signature,
            "message": "Signature valide ✓" if is_valid else "Signature invalide ✗"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )


# ============== ENDPOINT STATISTIQUES ==============

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Récupérer les statistiques de l'application"""
    total_clients = db.query(Client).count()
    total_factures = db.query(Facture).count()
    factures_signees = db.query(Facture).filter(Facture.est_signee == True).count()
    montant_total = db.query(Facture).with_entities(db.func.sum(Facture.montant_total)).scalar() or 0

    return {
        "total_clients": total_clients,
        "total_factures": total_factures,
        "factures_signees": factures_signees,
        "factures_non_signees": total_factures - factures_signees,
        "montant_total": float(montant_total),
        "taux_signature": round((factures_signees / total_factures * 100) if total_factures > 0 else 0, 2)
    }


# ============== ENDPOINT RACINE ==============

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "application": "Billing App with UOV Signature",
        "version": "1.0.0",
        "description": "Application de facturation avec signature numérique UOV (Unbalanced Oil and Vinegar)",
        "documentation": "/docs",
        "frontend": "Ouvrez frontend/index.html dans votre navigateur"
    }


# Point d'entrée pour lancer l'application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
