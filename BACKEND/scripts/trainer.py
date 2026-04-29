import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from generate_dat import generate_complex_data

def train_and_save():
    print("Démarrage de l'entraînement du modèle...")
    df = generate_complex_data()
    print(f"Données générées : {len(df)} échantillons")
    print("Aperçu des données :")
    print(df.head())
    # On définit nos Features (X) et notre Target (y)
    features = ['mois', 'carburant', 'dispo', 'indice_pol', 'indice_econ']
    X = df[features]
    y = df['prix']
    print(f"Features utilisées : {features}")
    

    # Division pour le test (pour calculer la précision)
    print("Division des données en train/test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Taille de l'ensemble d'entraînement : {len(X_train)}")

    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Entraînement du modèle
    # On augmente max_depth pour capturer la complexité des indices
    model = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Calcul de la précision (R² Score)
    precision = model.score(X_test_scaled, y_test)

    # Sauvegarde dans le dossier brain
    print("Sauvegarde du modèle et du scaler dans /brain...")
    os.makedirs('BACKEND/brain', exist_ok=True)
    joblib.dump(model, 'BACKEND/brain/model.pkl')
    joblib.dump(scaler, 'BACKEND/brain/scaler.pkl')
    # On stocke la précision pour que l'API puisse l'afficher
    joblib.dump(precision, 'BACKEND/brain/precision.pkl')

    print(f" Modèle entraîné !")
    print(f" Précision : {precision * 100:.2f}%")
    print(f" Fichiers sauvegardés dans BACKEND/brain/")
    # if __name__ == "__main__":
      # train_and_save()
train_and_save()      