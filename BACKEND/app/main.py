from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Depends
import joblib , os ,numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from .database import SessionLocal, engine, Base, get_db, seed_database
from dateutil.relativedelta import relativedelta
from .models import PredictionInput, PredictionLog , MarketIndex 
from datetime import date
from contextlib import asynccontextmanager
import pandas as pd
from app.database import SessionLocal

from scripts.scraper import update_market_indices_via_finance
from scripts.reality_simulator import simulate_market_reality
from scripts.match import sync_real_prices

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
        # Chargement des données JSON (Seeding)
        with SessionLocal() as db:
         seed_database(db)
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
async def predict(payload: PredictionInput , db: Session = Depends(get_db)):
    # Plus besoin de vérifier "if model is None", lifespan s'en est chargé !
    
    try:
        # Si predire_dans_x_mois est fourni (ex: 3), on l'ajoute à aujourd'hui
        if payload.predire_dans_x_mois and payload.predire_dans_x_mois > 0:
            target_date = date.today() + relativedelta(months=payload.predire_dans_x_mois)
        else:
            # Sinon on prend la date fournie, ou aujourd'hui par défaut
            target_date = payload.date_prediction or date.today()
        
        # 1. Encodage sécurisé du produit
        try:
            prod_name = payload.produit.capitalize()
            prod_encoded = brain["encoder"].transform([prod_name])[0]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Produit '{payload.produit}' inconnu.")

        context = {
            "carburant": 840.0, 
            "disponibilite": 1,
            "indice_politique": 0.5,
            "indice_economique": 0.8
        }
        # 2. On récupère les indices DEPUIS LA DB (ceux que le scraper a rempli)
        indices = db.query(MarketIndex).filter(
        MarketIndex.mois == target_date.month,
        MarketIndex.annee == target_date.year).first()
        # 3. Préparation des données
        # Sécurité : Si le scraper n'a pas encore rempli le mois futur, on prend le dernier connu
        if not indices:
          indices = db.query(MarketIndex).order_by(MarketIndex.annee.desc(), MarketIndex.mois.desc()).first()

    # 3. On prépare le dictionnaire pour le modèle ET pour le log
        # On définit des constantes par défaut au cas où la DB est vide
        DEFAULT_FUEL = 840.0
        DEFAULT_INDEX = 0.5

        input_data = {
                "carburant": indices.prix_carburant if indices else DEFAULT_FUEL,
                "disponibilite": 1, 
                "indice_politique": indices.indice_politique if indices else DEFAULT_INDEX,
                "indice_economique": indices.indice_economique if indices else DEFAULT_INDEX
                        }

    # 4. Conversion pour le modèle IA
        prod_encoded = brain["encoder"].transform([payload.produit])[0]
    
    # Création du DataFrame avec les noms exacts des colonnes pour le modèle
        X = pd.DataFrame([{
        "produit": prod_encoded,
        "mois": target_date.month,
        **input_data
    }])

    # 5. Inférence
        X_scaled = brain["scaler"].transform(X)
        prediction = brain["model"].predict(X_scaled)[0]

    # 6. ARCHIVAGE (C'est ici qu'on stocke ce qu'on a utilisé)
        log = PredictionLog(
        produit=payload.produit,
        date_voulue=target_date,
        prix_predit=prediction,
        input_features=input_data  # On garde une trace du prix du carburant utilisé !
    )
        db.add(log)
        db.commit()
        
        

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
        db.rollback() # Annule en cas d'erreur DB
        print(f" [SERVER ERROR] : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne de prédiction.{e}")
    
    
    
    
# def maintenance_cycle(db: Session):
#     # 1. Mise à jour des indices mondiaux
#     update_market_indices_via_finance()
    
#     # 2. Collecte de la réalité (Simulateur)
#     simulate_market_reality(db)
    
#     # 3. Synchronisation (Le Match)
#     sync_real_prices(db)
    
#     # 4. Vérification de la performance
#     perf = calculate_model_accuracy(db)
#     print(f"Précision actuelle : {perf}%")
    
#     # # 5. Condition de réentraînement
#     if perf < 85.0: # Si on descend sous 85% de précision
#         print(" Lancement du réentraînement du modèle...")
#         retrain_model_with_new_logs(db)
        
        
# def calculate_model_accuracy(db: Session):
#     """
#     Calcule la précision (Accuracy) basée sur les logs synchronisés.
#     """
#     # On récupère uniquement les prédictions qui ont été confrontées à la réalité
#     logs = db.query(PredictionLog).filter(PredictionLog.prix_reel != None).all()
    
#     if not logs:
#         print("📊 Pas assez de données pour calculer la précision.")
#         return 100.0 # On suppose que tout va bien si on n'a pas encore de preuves

#     total_mape = 0
#     for log in logs:
#         # Formule de l'erreur relative : |Prédit - Réel| / Réel
#         error = abs(log.prix_predit - log.prix_reel) / log.prix_reel
#         total_mape += error

#     # Moyenne des erreurs
#     mean_error = total_mape / len(logs)
#     accuracy = (1 - mean_error) * 100
    
#     print(f"📊 Précision actuelle du modèle : {round(accuracy, 2)}%")
#     return round(accuracy, 2)



# import pandas as pd
# import joblib
# from sklearn.ensemble import RandomForestRegressor

# def retrain_model_with_new_logs(db: Session):
#     """
#     Réentraîne le modèle en utilisant les logs de la DB comme nouveau dataset.
#     """
#     # 1. Extraction des données
#     query = db.query(PredictionLog).filter(PredictionLog.prix_reel != None)
#     df = pd.read_sql(query.statement, db.bind)

#     if len(df) < 10: # Seuil minimum pour ne pas entraîner sur du vide
#         print("⚠️ Trop peu de données pour un réentraînement sérieux.")
#         return

#     # 2. Préparation des Features (X) et de la Cible (y)
#     # On extrait les données du dictionnaire JSON 'input_features'
#     X = pd.DataFrame([
#         {
#             "produit": log.produit, # Attention : devra être encodé
#             "mois": log.date_voulue.month,
#             "carburant": log.input_features.get('carburant'),
#             "disponibilite": log.input_features.get('disponibilite', 1.0),
#             "indice_politique": log.input_features.get('indice_politique'),
#             "indice_economique": log.input_features.get('indice_economique')
#         } for log in db.query(PredictionLog).filter(PredictionLog.prix_reel != None).all()
#     ])
    
#     y = df['prix_reel']

#     # 3. Encodage (On utilise l'encodeur chargé au démarrage)
#     # Note: Dans un vrai flux, on ré-encode proprement les noms de produits
#     X['produit'] = brain["encoder"].transform(X['produit'])

#     # 4. Entraînement
#     print("🧠 Réentraînement du Random Forest en cours...")
#     new_model = RandomForestRegressor(n_estimators=100)
#     new_model.fit(X, y)

#     # 5. Sauvegarde (On écrase l'ancien ou on crée une v2)
#     model_path = os.path.join(BRAIN_DIR, "model.pkl")
#     joblib.dump(new_model, model_path)
    
#     # On met à jour le dictionnaire global pour que l'API utilise le nouveau cerveau tout de suite
#     brain["model"] = new_model
#     print("✅ Modèle mis à jour avec succès !")