from firebase_admin import credentials
import firebase_admin
from firebase_admin import firestore

cred = credentials.Certificate("auth.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
