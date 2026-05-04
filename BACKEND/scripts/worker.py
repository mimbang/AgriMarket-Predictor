# worker.py
from BACKEND.app.database import SessionLocal
from BACKEND.scripts.scraper import update_market_indices_via_finance
from BACKEND.scripts.reality_simulator import simulate_market_reality
from BACKEND.scripts.run_tasks import calculate_model_accuracy, retrain_model
from BACKEND.scripts.match import sync_real_prices

def main():
    db = SessionLocal()
    print("🚀 Démarrage de la maintenance...")

    # --- ÉTAPE 1 : SCRAPER ---
    try:
        print("🌐 [1/4] Mise à jour des indices mondiaux...")
        update_market_indices_via_finance(db)
        print("✅ Indices mis à jour.")
    except Exception as e:
        print(f"⚠️ Échec du scraper (mais on continue) : {e}")
        db.rollback() # Important pour nettoyer la transaction échouée

    # --- ÉTAPE 2 : RÉALITÉ ---
    try:
        print("📡 [2/4] Collecte des prix réels...")
        simulate_market_reality(db)
        sync_real_prices(db)
        print("✅ Réalité synchronisée.")
    except Exception as e:
        print(f"⚠️ Échec de la simulation : {e}")
        db.rollback()

    # --- ÉTAPE 3 : TRAINING ---
    # ... etc pour les autres étapes ...

    db.close()
    print("🏁 Fin du processus.")

if __name__ == "__main__":
    main()