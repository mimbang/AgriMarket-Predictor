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

from pydantic import BaseModel, Field, field_validator, validator
from typing import Optional

class PredictionInput(BaseModel):
    # L'utilisateur choisit uniquement le produit et l'échéance
    produit: str = Field(..., description="Le nom du produit agricole")
    date_prediction: Optional[date] = Field(
        None,
        description="Date de la prédiction"
    )
    predire_dans_x_mois: int = Field(
        default=0, 
        ge=0, 
        le=12, 
        description="Nombre de mois dans le futur (0 pour ce mois-ci)"
    )
    
    # Optionnel : une ville si tu veux affiner plus tard
    ville: Optional[str] = Field("Yaoundé", description="Ville de référence")

    @field_validator('produit')
    @classmethod
    def validate_produit(cls, v):
        # On normalise pour correspondre aux noms dans ton modèle IA
        v = v.capitalize()
        produits_autorises = ["Tomate", "Oignon", "Maïs", "Pomme de terre"]
        if v not in produits_autorises:
            raise ValueError(f"Produit non géré. Liste autorisée : {produits_autorises}")
        return v
    
    @field_validator('date_prediction', mode='before')
    @classmethod
    def validate_date_prediction(cls, v, values):
        if v is None:
            # Si l'utilisateur n'a pas fourni de date, on calcule à partir de 'predire_dans_x_mois'
            mois_a_ajouter = values.get('predire_dans_x_mois', 0)
            return (datetime.today() + relativedelta(months=mois_a_ajouter)).date()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "produit": "Tomate",
                "predire_dans_x_mois": 2,
                "ville": "Yaoundé"
            }
        }
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base


import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Date, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Product(Base):
    """
    TABLE : products
    ROLE  : Référentiel des produits supportés par l'IA.
    DOC   : Garantit que le front-end demande un produit existant et connu.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False) # Ex: "Tomate"
    categorie = Column(String)                        # Ex: "Légume"
    unite = Column(String, default="kg")              # Ex: "Kg" ou "Sac"

class MarketIndex(Base):
    """
    TABLE : market_indices
    ROLE  : Bibliothèque des variables économiques (Carburant, Stabilité).
    DOC   : Le Back-end consulte cette table pour nourrir l'IA automatiquement 
            sans que le Front n'ait à envoyer ces chiffres complexes.
    """
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)
    mois = Column(Integer, nullable=False)           # 1 à 12
    annee = Column(Integer, nullable=False)          # Ex: 2026
    prix_carburant = Column(Float, nullable=False)   # Prix du litre
    indice_politique = Column(Float, default=0.5)    # Score 0 à 1
    indice_economique = Column(Float, default=0.5)   # Score 0 à 1

class PredictionLog(Base):
    """
    TABLE : prediction_logs
    ROLE  : Journal de bord et Historique des prédictions.
    DOC   : Stocke chaque calcul effectué. L'UUID sécurise l'accès. 
            La colonne 'prix_reel' est mise à jour plus tard par le scraper.
    """
    __tablename__ = "prediction_logs"

    # UUID : Identifiant unique complexe (ex: 550e8400-e29b...)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Informations de la demande
    produit = Column(String, nullable=False)
    date_voulue = Column(Date, nullable=False)
    
    # Paramètres utilisés par l'IA (stockés en JSON pour audit)
    # Exemple : {"carburant": 850, "indice_pol": 0.5}
    input_features = Column(JSON) 
    
    # Résultats
    prix_predit = Column(Float, nullable=False)
    prix_reel = Column(Float, nullable=True) # Rempli a posteriori par le scraper
    model_version = Column(String, default="v1.0_rf")

class ScrapedPrice(Base):
    """
    TABLE : scraped_prices
    ROLE  : Mémoire des relevés réels sur le terrain.
     Contient les prix trouvés par ton scraper. 
            Sert à remplir 'prix_reel' dans 'prediction_logs'.
    """
    __tablename__ = "scraped_prices"

    id = Column(Integer, primary_key=True, index=True)
    date_releve = Column(Date, nullable=False)
    produit = Column(String, nullable=False)
    prix_constate = Column(Float, nullable=False)
    source = Column(String) # Nom du marché ou site web        