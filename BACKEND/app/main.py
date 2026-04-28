from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
import time

app = FastAPI()

# AU DÉMARRAGE : On crée les tables si elles n'existent pas
# C'est la méthode "simple" avant de passer à Alembic
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