import os
from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# On force le chargement du .env (utile pour le dev local hors docker)
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL n'est pas défini dans le .env")

# Le "moteur" qui parle à la DB
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Une "usine" à sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fonction pour obtenir une connexion (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
        
import json
import os
from sqlalchemy.orm import Session
from .models import MarketIndex, Product

def seed_database(db: Session):
    if not os.path.exists("seed_data.json"):
        print(" Aucun fichier seed_data.json trouvé.")
        return

    with open("seed_data.json", "r") as f:
        data = json.load(f)

    # Remplir Market Indices
    if db.query(MarketIndex).count() == 0:
        for item in data["market_indices"]:
            db.add(MarketIndex(**item))
        print(" Market indices chargés.")

    # Remplir Products
    if db.query(Product).count() == 0:
        for item in data["products"]:
            db.add(Product(**item))
        print(" Produits chargés.")

    db.commit()