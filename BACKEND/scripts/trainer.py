import pandas as pd
import joblib
import os
from generate_dat import generate_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder

def train_from_csv():
    # csv_path = 'Persitent_storage/data.csv'
    # if not os.path.exists(csv_path):
    #     print("❌ Erreur : Le fichier data.csv est introuvable. Lancez generate_dat.py d'abord.")
    #     return

    print("🧠 Apprentissage en cours à partir du CSV...")
    # df = pd.read_csv(csv_path)
    
    df = generate_data()  # Génère un nouveau dataset à chaque entraînement (optionnel, à adapter selon tes besoins)
    df = df.dropna()  # On élimine les lignes avec des valeurs manquantes (si jamais il y en a)
    # 1. Encodage du texte (Produit)
    le = LabelEncoder()
    df["produit_encoded"] = le.fit_transform(df['produit'])

    # 2. Préparation des Features
    X = df[['produit_encoded', 'mois', 'carburant', 'dispo', 'pol', 'econ']]
    y = df['prix']

    # 3. Normalisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. Modèle
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # 5. Sauvegarde
    os.makedirs('brain', exist_ok=True)
    joblib.dump(model, 'brain/model.pkl')
    joblib.dump(scaler, 'brain/scaler.pkl')
    joblib.dump(le, 'brain/label_encoder.pkl')
    joblib.dump(model.score(X_scaled, y), 'brain/precision.pkl')

    print(f"✅ Modèle sauvegardé dans /brain ! Précision : {model.score(X_scaled, y)*100:.2f}%")

if __name__ == "__main__":
    train_from_csv()