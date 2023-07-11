from db import db


def save_votes(votesList):
    for vote in votesList:
        doc_ref = db.collection('votes').document()
        doc_ref.set(vote)

def get_votes():
    all_votes = []

    users_ref = db.collection("votes")
    docs = users_ref.stream()

    all_votes.extend([doc.to_dict() for doc in docs])

    return all_votes