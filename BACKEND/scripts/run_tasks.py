import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy.orm import Session
from app.models import PredictionLog

BRAIN_DIR = "brain"

def calculate_model_accuracy(db: Session):
    logs = db.query(PredictionLog).filter(PredictionLog.prix_reel != None).all()
    if not logs: return 100.0
    
    # Calcul de l'erreur absolue moyenne en % (MAPE)
    errors = [abs(l.prix_predit - l.prix_reel) / l.prix_reel for l in logs]
    accuracy = (1 - (sum(errors) / len(errors))) * 100
    return round(accuracy, 2)

def retrain_model(db: Session):
    # Extraction propre pour le réentraînement
    logs = db.query(PredictionLog).filter(PredictionLog.prix_reel != None).all()
    
    data = []
    for log in logs:
        # On aplatit le JSON input_features et on ajoute la cible
        row = {**log.input_features, "target": log.prix_reel, "mois": log.date_voulue.month}
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Prétraitement (X, y)
    X = df.drop(columns=['target', 'ville']) # On retire la ville si pas encore encodée
    y = df['target']
    
    # Entraînement
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    # Sauvegarde versionnée pour la prod (sécurité)
    version = pd.Timestamp.now().strftime("%Y%m%d")
    path = os.path.join(BRAIN_DIR, f"model_{version}.pkl")
    joblib.dump(model, path)
    
    # On met à jour le lien symbolique "latest"
    latest_path = os.path.join(BRAIN_DIR, "model.pkl")
    if os.path.exists(latest_path): os.remove(latest_path)
    os.symlink(path, latest_path)
    
    return path