def article_exists(db, url):
    docs = db.collection("raw_articles").where("url", "==", url).limit(1).stream()
    return any(docs)