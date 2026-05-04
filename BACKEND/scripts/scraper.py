import yfinance as yf
from datetime import datetime
from BACKEND.app.database import SessionLocal
from BACKEND.app.models import MarketIndex

def update_market_indices_via_finance():
    """
    Récupère le cours du Pétrole Brent et met à jour la base de données.
    C'est gratuit, sans clé, et extrêmement fiable.
    """
    try:
        # BZ=F est le symbole du Pétrole Brent sur Yahoo Finance
        ticker = yf.Ticker("BZ=F")
        
        # On récupère le dernier prix de clôture
        data = ticker.history(period="1d")
        if data.empty:
            print(" Impossible de récupérer les données boursières.")
            return

        last_price_usd = data['Close'].iloc[-1]
        # FORMULE DE SIMULATION :
        # On ajuste pour que 80$ (Brent) devienne ~840 FCFA (Pompe)
        # Ratio = 840 / 80 = 10.5
        simulated_price = round(last_price_usd * 10.5, 2)
        
        # Conversion USD -> FCFA (approximative ou via un taux fixe)
        # Actuellement 1 USD ~ 600 FCFA
        price_fcfa = round(simulated_price * 605, 2)

        # --- MISE À JOUR BASE DE DONNÉES ---
        db = SessionLocal()
        now = datetime.now()
        
        index = db.query(MarketIndex).filter_by(mois=now.month, annee=now.year).first()

        if index:
            index.prix_carburant = price_fcfa
            print(f" Brent mis à jour : {price_fcfa} FCFA (équivalent baril)")
        else:
            new_index = MarketIndex(
                mois=now.month, 
                annee=now.year, 
                prix_carburant=price_fcfa,
                indice_politique=0.5,
                indice_economique=0.5
            )
            db.add(new_index)
            print(f"✅ Nouveau mois créé avec le Brent : {price_fcfa} FCFA")

        db.commit()
        db.close()

    except Exception as e:
        print(f"🔥 Erreur yfinance : {e}")


def get_simulated_local_fuel():
    ticker = yf.Ticker("BZ=F")
    data = ticker.history(period="1d")
    print(" Récupération du cours du Brent pour simuler le prix du carburant local...")
    
    if not data.empty:
        print(" Données boursières récupérées pour la simulation.")
        print(f" Dernier prix du Brent (USD) : {data['Close'].iloc[-1]}")
        last_price_usd = data['Close'].iloc[-1]
        
        # FORMULE DE SIMULATION :
        # On ajuste pour que 80$ (Brent) devienne ~840 FCFA (Pompe)
        # Ratio = 840 / 80 = 10.5
        simulated_price = round(last_price_usd * 10.5, 2)
        print(f" Prix simulé du carburant local : {simulated_price} FCFA (équivalent baril)")
        
        return simulated_price
    print(" Impossible de récupérer les données boursières pour la simulation. Retour à une valeur par défaut.")
    print(" Valeur par défaut utilisée : 840 FCFA")
    return 840.0 # Fallback constant

if __name__ == "__main__":
        get_simulated_local_fuel()