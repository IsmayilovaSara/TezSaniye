from firestore_client import initialize_firestore

db = initialize_firestore()

count = sum(1 for _ in db.collection("raw_articles").stream())

print("Total articles:", count)