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