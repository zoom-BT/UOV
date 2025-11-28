from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Client(Base):
    """Modèle pour les clients"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    adresse = Column(String)
    telephone = Column(String)
    date_creation = Column(DateTime, default=datetime.utcnow)

    # Relation avec les factures
    factures = relationship("Facture", back_populates="client")


class Facture(Base):
    """Modèle pour les factures"""
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    numero_facture = Column(String, unique=True, nullable=False)
    date_emission = Column(DateTime, default=datetime.utcnow)
    montant_total = Column(Float, nullable=False)
    description = Column(String)
    items = Column(String)  # JSON string pour les items de la facture

    # Champs de signature UOV
    signature_uov = Column(LargeBinary, nullable=True)
    cle_publique = Column(LargeBinary, nullable=True)
    cle_privee = Column(LargeBinary, nullable=True)
    est_signee = Column(Boolean, default=False)
    date_signature = Column(DateTime, nullable=True)

    date_creation = Column(DateTime, default=datetime.utcnow)

    # Relation avec le client
    client = relationship("Client", back_populates="factures")
