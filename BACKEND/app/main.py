from fastapi import FastAPI, Depends
import joblib
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
import time
from .models import PredictionInput
from datetime import date

app = FastAPI(title="My Predictor MArket")

# AU DÉMARRAGE : On crée les tables si elles n'existent pas
# C'est la méthode "simple" avant de passer à Alembic
# 2. Chargement du cerveau (si les fichiers existent)
try:
    model = joblib.load("brain/model.pkl")
    scaler = joblib.load("brain/scaler.pkl")
    precision = joblib.load("brain/precision.pkl")
except:
    model = None
    print("⚠️ Attention : Modèle non trouvé dans /brain")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données connectée et tables créées !")
except Exception as e:
    print(f"❌ Erreur de connexion à la DB : {e}")

@app.get("/")
def read_root():
    return {"status": "L'API est en ligne", "intelligence": "AgriPredict Pro v1"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    # Si cette route répond, c'est que la boucle API -> DB fonctionne
    return {"status": "Connexion DB opérationnelle"}

@app.post("/predict")
def predict_price(payload: PredictionInput):
    # Extraction de la date et du mois
    target_date = payload.date_prediction or date.today()
    target_month = target_date.month
    
    # Préparation des données pour l'IA
    # L'ordre doit être EXACTEMENT le même que lors de l'entraînement
    features = [
        target_month, 
        payload.carburant, 
        payload.disponibilite, 
        payload.indice_politique, 
        payload.indice_economique
    ]
    
    # (Ensuite on appelle le scaler et le modèle...)
    return {"message": f"Analyse pour le mois {target_month} lancée"}