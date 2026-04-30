import pandas as pd
import numpy as np
import os

def generate_data():
    print("🚜 Génération du dataset Agri-Cameroun...")
    np.random.seed(42)
    n_per_product = 2500
    
    products_config = {
        "Oignon": {"base": 25000, "sens": 1.5, "soudure": [3, 4, 5, 6]},
        "Tomate": {"base": 5000, "sens": 2.5, "soudure": [7, 8, 9]},
        "Maïs":   {"base": 18000, "sens": 1.2, "soudure": [4, 5, 6]},
        "Pomme de terre": {"base": 22000, "sens": 1.4, "soudure": [5, 6, 7]}
    }

    all_rows = []
    for prod, conf in products_config.items():
        months = np.random.randint(1, 13, n_per_product)
        carburant = np.random.uniform(600, 950, n_per_product)
        dispo = np.random.uniform(0.1, 1.0, n_per_product)
        pol = np.random.uniform(0.4, 1.0, n_per_product)
        econ = np.random.uniform(0.4, 1.0, n_per_product)

        # Logique de prix
        price = conf["base"] + (carburant * 5)
        price += (1 / dispo) * (500 * conf["sens"])
        price *= np.where(np.isin(months, conf["soudure"]), 1.4, 1.0)
        price *= (1.3 - (pol * 0.3))
        price += np.random.normal(0, conf["base"] * 0.05, n_per_product)

        for i in range(n_per_product):
            all_rows.append([prod, months[i], carburant[i], dispo[i], pol[i], econ[i], round(price[i], 2)])

    df = pd.DataFrame(all_rows, columns=['produit', 'mois', 'carburant', 'dispo', 'pol', 'econ', 'prix'])
    
    os.makedirs('Persitent_storage', exist_ok=True)
    df.to_csv('Persitent_storage/data.csv', index=False)
    print(f"💾 Dataset sauvegardé : {len(df)} lignes dans Persitent_storage/data.csv")
    return df

if __name__ == "__main__":
    generate_data()