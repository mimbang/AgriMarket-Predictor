import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_initial_model():
    # 1. Chargement (Ici tu mettras le chemin vers ton CSV Kaggle)
    # Pour l'exemple, on crée des données fictives qui ressemblent à ton marché
    data = {
        'prix_carburant': np.random.uniform(500, 800, 1000),
        'disponibilite': np.random.uniform(0, 1, 1000),
        'prix_reel': np.random.uniform(200, 1000, 1000)
    }
    df = pd.DataFrame(data)

    # --- LE NETTOYAGE (Anti-Valeurs Aberrantes) ---
    # On retire ce qui est à plus de 3 écarts-types (Méthode Z-score simple)
    df = df[(np.abs(df['prix_reel'] - df['prix_reel'].mean()) <= (3 * df['prix_reel'].std()))]

    X = df[['prix_carburant', 'disponibilite']]
    y = df['prix_reel']

    # 2. Prétraitement
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Entraînement
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # 4. Exportation (Vers le dossier brain que Docker partage avec l'API)
    os.makedirs('brain', exist_ok=True)
    joblib.dump(model, 'brain/model.pkl')
    joblib.dump(scaler, 'brain/scaler.pkl')
    
    print("✅ Modèle et Scaler générés dans BACKEND/brain/")

if __name__ == "__main__":
    train_initial_model()