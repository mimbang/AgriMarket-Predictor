from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Depends
import joblib , os ,numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from .database import engine, Base, get_db
import time
from .models import PredictionInput
from datetime import date
from contextlib import asynccontextmanager
import pandas as pd

# app = FastAPI(title="AgriMarket API")
load_dotenv()

# --- CONFIGURATION ---
BRAIN_DIR = os.getenv("BRAIN_DIR", "brain")
paths = {
    "model": os.path.join(BRAIN_DIR, os.getenv("MODEL_NAME", "model.pkl")),
    "scaler": os.path.join(BRAIN_DIR, os.getenv("SCALER_NAME", "scaler.pkl")),
    "encoder": os.path.join(BRAIN_DIR, os.getenv("ENCODER_NAME", "label_encoder.pkl")),
    "precision": os.path.join(BRAIN_DIR, os.getenv("PRECISION_NAME", "precision.pkl"))
}

# Dictionnaire global pour stocker nos modèles chargés
brain = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Gestion du cycle de vie : Chargement des modèles avant le démarrage """
    print("\n" + "="*50)
    print(" [STARTUP] Initialisation des systèmes IA...")
    
    
    # 1. TEST DE LA BASE DE DONNÉES
    try:
        print("📡 [DB] Connexion à PostgreSQL...")
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL is None:
            raise ValueError("DATABASE_URL n'est pas défini dans le .env")
        engine = create_engine(DATABASE_URL, connect_args={'connect_timeout': 5})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(" [DB] Base de données connectée et prête.")
    except Exception as e:
        print(f" [DB] Erreur : Impossible de joindre la base de données.")
        print(f"👉 Détail : {e}")
    
    # Vérification de présence
    try:
        # On définit explicitement les chemins
        model_path = os.path.join(BRAIN_DIR, "model.pkl")
        scaler_path = os.path.join(BRAIN_DIR, "scaler.pkl")
        encoder_path = os.path.join(BRAIN_DIR, "label_encoder.pkl")
        precision_path = os.path.join(BRAIN_DIR, "precision.pkl")

        # Vérification chirurgicale
        for name, p in [("model", model_path), ("scaler", scaler_path), ("encoder", encoder_path), ("precision", precision_path)]:
            if not os.path.exists(p):
                print(f" [IA] Fichier manquant : {p}")
                # On lève une erreur pour arrêter le serveur si un fichier manque
                raise FileNotFoundError(f"Le fichier {name} est introuvable.")
            
            # Chargement dans le dictionnaire global brain
            brain[name] = joblib.load(p)
            print(f" [IA] {name.capitalize()} chargé.")

        print("💎 [IA] Système prêt pour les prédictions.")

    except Exception as e:
        print(f" [CRITICAL] Échec du démarrage IA : {e}")
        # On ne yield pas, le serveur s'arrête proprement
        raise e

    print("═"*50 + "\n")
    yield
    brain.clear()
    print(" [SHUTDOWN] Libération de la mémoire.")

app = FastAPI(
    title="My Predictor MArket",
    lifespan=lifespan  # Indispensable pour charger le cerveau au démarrage !
)

# --- ROUTES ---
@app.get("/")
def read_root():
    return {"status": "L'API est en ligne", "intelligence": "AgriPredict Pro v1"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    # Si cette route répond, c'est que la boucle API -> DB fonctionne
    return {"status": "Connexion DB opérationnelle"}

@app.post("/predict")
async def predict(payload: PredictionInput):
    # Plus besoin de vérifier "if model is None", lifespan s'en est chargé !
    
    try:
        # 1. Encodage sécurisé du produit
        try:
            prod_name = payload.produit.capitalize()
            prod_encoded = brain["encoder"].transform([prod_name])[0]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Produit '{payload.produit}' inconnu.")

        # 2. Préparation des données
        target_date = payload.date_prediction or date.today()
        
        features = np.array([[
            prod_encoded, 
            target_date.month, 
            payload.carburant, 
            payload.disponibilite, 
            payload.indice_politique, 
            payload.indice_economique
        ]])
        # Remplace la création du np.array par un DataFrame avec les bons noms
        features_df = pd.DataFrame([{
                 "produit": prod_encoded,
                     "mois": target_date.month,
                     "carburant": payload.carburant,
                    "disponibilite": payload.disponibilite,
                    "indice_politique": payload.indice_politique,
            "indice_economique": payload.indice_economique
        }])

            # L'inférence se fait maintenant sans Warning
        features_scaled = brain["scaler"].transform(features_df)
        
        
        # 3. Inférence
        # features_scaled = brain["scaler"].transform(features)
        prediction = brain["model"].predict(features_scaled)[0]

        print(f" [PREDICT] {prod_name}: {round(prediction, 2)} FCFA")

        return {
            "status": "success",
            "prediction": round(float(prediction), 2),
            "meta": {
                "confiance": f"{round(brain['precision'] * 100, 2)}%",
                "date": target_date
            }
        }

    except HTTPException: raise
    except Exception as e:
        print(f" [SERVER ERROR] : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne de prédiction.{e}")