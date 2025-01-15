import firebase_admin
from firebase_admin import credentials, firestore


def init_db():
    try:
        cred = credentials.Certificate("src/data/sources/firebase/firebase.json")
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception:
        print("Error iniciando la base de datos")

db = init_db()