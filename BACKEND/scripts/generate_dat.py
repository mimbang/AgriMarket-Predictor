import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_complex_data():
    np.random.seed(42)
    n = 5000  # On augmente pour plus de précision
    
    # 1. Variables de base
    months = np.random.randint(1, 13, n)
    carburant = np.random.uniform(600, 950, n)  # Prix à la pompe
    dispo = np.random.uniform(0.05, 1.0, n)     # 0.05 = pénurie totale
    
    # 2. Nouveaux Indices (0 à 1)
    # Indice Politique : 0 (conflit/routes barrées) à 1 (stabilité totale)
    indice_pol = np.random.uniform(0, 1, n)
    
    # Indice Economique : 0 (forte inflation/crise) à 1 (croissance stable)
    indice_econ = np.random.uniform(0, 1, n)

    # 3. Logique Métier "Cameroun"
    # Le prix de base est dicté par le carburant
    prix_base = carburant * 0.6
    
    # Impact de la disponibilité (exponentiel : quand c'est rare, ça explose)
    impact_rarete = (1 / (dispo + 0.1)) * 45
    
    # Impact Saisonnalité (Soudure entre Mars et Juin : les stocks sont vides)
    impact_saison = np.where((months >= 3) & (months <= 6), 1.45, 1.0)
    
    # Impact Politique & Economique
    # Si pol est bas (0.2), le prix augmente car l'approvisionnement est risqué
    impact_externe = (1.5 - (indice_pol * 0.3)) * (1.3 - (indice_econ * 0.2))
    
    # Calcul du prix final avec un bruit aléatoire réaliste
    prix_reel = (prix_base + impact_rarete) * impact_saison * impact_externe
    prix_reel += np.random.normal(0, 25, n)

    return pd.DataFrame({
        'mois': months,
        'carburant': carburant,
        'dispo': dispo,
        'indice_pol': indice_pol,
        'indice_econ': indice_econ,
        'prix': prix_reel
    })
