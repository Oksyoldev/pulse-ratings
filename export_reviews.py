import os
import shutil
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

# Папка с аватарами в репозитории
AVATARS_DIR = "avatars"
if not os.path.exists(AVATARS_DIR):
    os.makedirs(AVATARS_DIR)

def get_reviews_by_type(course_type: str, limit=20):
    cursor = reviews_collection.find(
        {"status": "approved", "course_type": course_type}
    ).sort("created_at", -1).limit(limit)
    
    reviews = []
    for r in cursor:
        photo_filename = r.get("photo_filename")
        # Копируем фото из папки бота в папку репозитория
        if photo_filename:
            src_path = f"/путь/до/бот/avatars/{photo_filename}"  # УКАЖИ ПУТЬ!
            dst_path = os.path.join(AVATARS_DIR, photo_filename)
            if os.path.exists(src_path) and not os.path.exists(dst_path):
                shutil.copy2(src_path, dst_path)
        
        reviews.append({
            "name": r.get("username", "Пользователь"),
            "review": r.get("review", ""),
            "rating": r.get("rating"),
            "photo_url": f"avatars/{photo_filename}" if photo_filename else None,
            "date": r.get("created_at").isoformat() if r.get("created_at") else None
        })
    return reviews

# Экспорт
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
print(f"[OK] Фото скопированы в {AVATARS_DIR}")
