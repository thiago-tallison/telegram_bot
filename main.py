from db import db

docs = db.collection('votos').stream()

for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
