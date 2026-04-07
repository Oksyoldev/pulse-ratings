import os
import json
from pymongo import MongoClient
from datetime import datetime

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "pulse")

if not MONGO_URL:
    print("❌ Ошибка: MONGO_URL не задан")
    exit(1)

print(f"✅ Подключаюсь к MongoDB...")
client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
users_collection = db["users"]

def get_course_stats(course_type):
    pipeline = [
        {"$match": {f"rating_{course_type}": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": None,
            "average": {"$avg": f"$rating_{course_type}"},
            "count": {"$sum": 1}
        }}
    ]
    result = list(users_collection.aggregate(pipeline))
    if result:
        return round(result[0]["average"], 1), result[0]["count"]
    return 0, 0

free_avg, free_count = get_course_stats("free")
pro_avg, pro_count = get_course_stats("pro")

stats = {
    "free": {"average": free_avg, "count": free_count},
    "pro": {"average": pro_avg, "count": pro_count},
    "updated_at": datetime.utcnow().isoformat()
}

with open("rating_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"✅ Бесплатный курс: {free_avg}⭐ ({free_count} оценок)")
print(f"✅ Платный курс: {pro_avg}⭐ ({pro_count} оценок)")
print(f"📅 Время: {stats['updated_at']}")
