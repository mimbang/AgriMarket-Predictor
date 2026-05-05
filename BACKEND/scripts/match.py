from sqlalchemy.orm import Session

from app.models import PredictionLog
from app.models import PredictionLog, ScrapedPrice

def sync_real_prices(db: Session):
    # 1. On cherche les logs qui n'ont pas encore de prix réel
    pending_logs = db.query(PredictionLog).filter(PredictionLog.prix_reel == None).all()
    
    for log in pending_logs:
        # 2. On cherche dans les prix scrapés si on a un match (Produit + Date)
        real_price = db.query(ScrapedPrice).filter(
            ScrapedPrice.produit == log.produit,
            ScrapedPrice.date_releve == log.date_voulue
        ).first()
        
        # 3. Si on trouve, on met à jour le log
        if real_price:
            log.prix_reel = real_price.prix_constate
            print(f" Match trouvé pour {log.produit} le {log.date_voulue}")
    
    db.commit()