import os
import json
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "pulse")

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
reviews_collection = db["reviews"]

def get_reviews(limit=20):
    """Получает последние 20 ОДОБРЕННЫХ отзывов"""
    cursor = reviews_collection.find(
        {"status": "approved"}  # Только одобренные!
    ).sort("created_at", -1).limit(limit)
    
    reviews = []
    for r in cursor:
        reviews.append({
            "username": r.get("username", "Аноним"),
            "review": r.get("review", ""),
            "rating": r.get("rating"),
            "date": r.get("created_at").isoformat() if r.get("created_at") else None
        })
    return reviews

reviews = get_reviews()

output = {
    "reviews": reviews,
    "total": len(reviews),
    "updated_at": datetime.utcnow().isoformat()
}

with open("reviews.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Экспортировано {len(reviews)} отзывов")
