# worker.py
from BACKEND.app.database import SessionLocal
from BACKEND.scripts.scraper import update_market_indices_via_finance
from BACKEND.scripts.reality_simulator import simulate_market_reality
from BACKEND.scripts.run_tasks import calculate_model_accuracy, retrain_model
from BACKEND.scripts.match import sync_real_prices

def run_daily_pipeline():
    db = SessionLocal()
    try:
        print("🚀 [1/4] Mise à jour des indices mondiaux...")
        update_market_indices_via_finance()
        
        print("📡 [2/4] Collecte des prix réels...")
        simulate_market_reality(db)
        sync_real_prices(db)
        
        print("📊 [3/4] Analyse de la précision...")
        acc = calculate_model_accuracy(db)
        print(f"Précision actuelle : {acc}%")
        
        if acc < 85.0:
            print("🧠 [4/4] Précision faible. Réentraînement lancé...")
            new_path = retrain_model(db)
            print(f"Nouveau modèle déployé : {new_path}")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_daily_pipeline()