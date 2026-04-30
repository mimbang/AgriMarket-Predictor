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
    
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class PredictionInput(BaseModel):
    # 1. Le Produit (avec une liste de choix pour éviter les erreurs de frappe)
    produit: str = Field(..., description="Nom du produit (Tomate, Oignon, Maïs, Pomme de terre)")
    
    # 2. Les Facteurs de Marché (avec limites strictes)
    carburant: float = Field(..., gt=0, le=2000, description="Prix du litre de carburant en FCFA")
    disponibilite: float = Field(..., ge=0.1, le=1.0, description="Niveau de stock (0.1: Pénurie, 1.0: Abondance)")
    
    # 3. Les Indices Macro (Valeurs par défaut à 0.5 pour un état 'moyen')
    indice_politique: float = Field(0.5, ge=0, le=1, description="Stabilité (0: Crise/Routes barrées, 1: Calme)")
    indice_economique: float = Field(0.5, ge=0, le=1, description="Santé éco (0: Forte inflation, 1: Stabilité)")
    
    # 4. La Gestion du Temps (Flexible)
    date_prediction: Optional[date] = None
    predire_dans_x_mois: Optional[int] = Field(None, ge=0, description="Nombre de mois à ajouter à aujourd'hui")

    @validator('produit')
    def check_product_exists(cls, v):
        # On s'assure que le produit est bien capitalisé comme dans le trainer
        v = v.capitalize()
        allowed = ["Tomate", "Oignon", "Maïs", "Pomme de terre"]
        if v not in allowed:
            raise ValueError(f"Produit non supporté. Choisissez parmi : {allowed}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "produit": "Tomate",
                "carburant": 840.0,
                "disponibilite": 0.4,
                "indice_politique": 0.7,
                "indice_economique": 0.5,
                "predire_dans_x_mois": 6
            }
        }