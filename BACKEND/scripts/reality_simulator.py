import random
from datetime import date
from sqlalchemy.orm import Session
from BACKEND.app.models import PredictionLog, ScrapedPrice

def simulate_market_reality(db: Session):
    """
    Simule la collecte de prix réels basée sur les prédictions existantes.
    Utile pour valider le pipeline avant d'avoir un vrai scraper.
    """
    # 1. On récupère les produits uniques que l'on a tenté de prédire
    pending_preds = db.query(PredictionLog).filter(PredictionLog.prix_reel == None).all()
    
    products_to_verify = set([p.produit for p in pending_preds])
    
    for prod_name in products_to_verify:
        # On simule un prix réel (Prix prédit +/- 5% à 10%)
        # En vrai, on prendrait la dernière prédiction pour ce produit
        last_pred = db.query(PredictionLog).filter_by(produit=prod_name).first()
        
        if last_pred:
            variation = random.uniform(0.9, 1.1) # Variation de 10%
            real_price = round(last_pred.prix_predit * variation, 2)
            
            # On enregistre ce "prix constaté" dans la table scraped_prices
            new_reality = ScrapedPrice(
                date_releve=date.today(),
                produit=prod_name,
                prix_constate=real_price,
                source="Simulateur_Terrain"
            )
            db.add(new_reality)
    
    db.commit()
    print(" Réalité simulée pour les produits en attente.")