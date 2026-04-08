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

def get_reviews_by_type(course_type: str, limit=20):
    cursor = reviews_collection.find(
        {"status": "approved", "course_type": course_type}
    ).sort("created_at", -1).limit(limit)
    
    reviews = []
    for r in cursor:
        photo_filename = r.get("photo_filename")
        reviews.append({
            "name": r.get("username", "Пользователь"),
            "review": r.get("review", ""),
            "rating": r.get("rating"),
            "photo_url": f"https://raw.githubusercontent.com/Oksyoldev/pulse-ratings/main/avatars/{photo_filename}" if photo_filename else None,
            "date": r.get("created_at").isoformat() if r.get("created_at") else None
        })
    return reviews

free_reviews = get_reviews_by_type("free")
pro_reviews = get_reviews_by_type("pro")

output = {
    "free": {"reviews": free_reviews, "total": len(free_reviews)},
    "pro": {"reviews": pro_reviews, "total": len(pro_reviews)},
    "updated_at": datetime.utcnow().isoformat()
}

with open("reviews.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"[OK] Экспортировано: бесплатных {len(free_reviews)}, платных {len(pro_reviews)}")
