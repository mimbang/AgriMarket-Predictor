from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MarketLog(Base):
    __tablename__ = "market_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Données de la requête
    produit = Column(String, index=True)
    date_voulue = Column(Date, index=True)
    
    # Variables d'entrée (Features)
    prix_carburant = Column(Float,nullable=True)
    disponibilite = Column(Float, nullable=True)
    impact_transport = Column(Float ,nullable = True)
    
    # Résultats
    prix_predit = Column(Float)
    prix_reel = Column(Float, nullable=True) # Sera rempli par le scraper
    
    # Méta-données de santé
    model_version = Column(String)
    is_valid = Column(Boolean, default=True)
    
    
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class PredictionInput(BaseModel):
    # Variables obligatoires
    carburant: float = Field(..., gt=0, description="Prix du carburant à la pompe (FCFA)")
    disponibilite: float = Field(..., ge=0, le=1, description="Indice de disponibilité (0: Pénurie, 1: Abondance)")
    
    # Variables avec valeurs par défaut (Indices)
    indice_politique: Optional[float] = Field(0.5, ge=0, le=1, description="Stabilité des routes/climat (0 à 1)")
    indice_economique: Optional[float] = Field(0.5, ge=0, le=1, description="Santé de l'économie/inflation (0 à 1)")
    
    # Date optionnelle (si absente, on prendra la date du jour dans le code)
    date_prediction: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "carburant": 840.0,
                "disponibilite": 0.3,
                "indice_politique": 0.7,
                "indice_economique": 0.5,
                "date_prediction": "2026-12-15"
            }
        }