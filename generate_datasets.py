import pandas as pd
import numpy as np
from datetime import datetime

def generate_agri_data(n_days=730): # 2 ans de données
    np.random.seed(42) # Pour que tes résultats soient reproductibles
    
    # 1. Création de la plage de dates
    dates = pd.date_range(start="2024-01-01", periods=n_days, freq='D')
    produits = ['Tomate', 'Oignon']
    marches = ['Mokolo', 'Sandaga']
    
    data = []

    for d in dates:
        for p in produits:
            for m in marches:
                mois = d.month
                
                # --- LOGIQUE MÉTIER ---
                
                # A. Définition de la Saison
                saison = "Seche" if mois in [11, 12, 1, 2, 3] else "Pluies"
                
                # B. Simulation Carburant (Inflation progressive)
                # On simule une hausse légère au fil du temps
                base_fuel = 840
                inflation_fuel = (d.year - 2024) * 50 + np.random.normal(0, 10)
                prix_carb = base_fuel + inflation_fuel
                
                # C. Indice de Disponibilité (0 à 10)
                if p == 'Tomate':
                    # Très dispo en début d'année, rare en plein milieu des pluies
                    dispo = 8 if mois in [1, 2, 3] else (3 if mois in [7, 8, 9] else 5)
                else: # Oignon
                    # Dispo après récolte Nord, rare en fin d'année
                    dispo = 9 if mois in [2, 3, 4] else (2 if mois in [9, 10, 11] else 5)
                
                # D. CALCUL DU PRIX (La Target)
                # Base : Tomate (cageot) ~10k, Oignon (sac) ~50k
                base_p = 10000 if p == 'Tomate' else 50000
                
                # Multiplicateurs
                mult_saison = 1.5 if (saison == "Pluies" and p == "Tomate") else 1.2
                mult_dispo = 2.0 - (dispo / 10) # Plus dispo est bas, plus le prix monte
                
                prix_final = base_p * mult_saison * mult_dispo
                
                # Impact Carburant (plus fort pour l'oignon qui vient du Nord)
                sensibilite = 1.2 if p == 'Oignon' else 0.6
                prix_final += (prix_carb - 840) * sensibilite
                
                # Ajout de bruit aléatoire (5%)
                prix_final += np.random.normal(0, prix_final * 0.05)
                
                data.append({
                    'Date': d,
                    'Produit': p,
                    'Marche': m,
                    'Saison': saison,
                    'Prix_Carburant': round(prix_carb, 2),
                    'Disponibilite': dispo,
                    'Prix_Vente': round(prix_final, -1) # Arrondi à la dizaine
                })

    return pd.DataFrame(data)

# Génération et sauvegarde
df = generate_agri_data()
df.to_csv('agrimarket_data_v1.csv', index=False)

print(f"Dataset généré : {df.shape[0]} lignes.")
print(df.head())

print("============")
print("Résumé des prix de vente :")
print(df['Prix_Vente'].describe())
print("============")
print("Distribution des produits :")
print(df['Produit'].value_counts())
print("============")
print("Distribution des marchés :")
print(df['Marche'].value_counts())
print("============")
print("Distribution des saisons :")
print(df['Saison'].value_counts())
print("============")
print("Corrélation entre prix de vente et prix carburant :")
print(df[['Prix_Vente', 'Prix_Carburant']].corr())
print("============")
print("Exemple de prix de vente en fonction de la disponibilité :")
print(df.groupby('Disponibilite')['Prix_Vente'].mean())
print("============")
print("Prix de vente moyen par produit :")
print(df.groupby('Produit')['Prix_Vente'].mean())