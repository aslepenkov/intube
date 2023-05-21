import json
from modules.utils import is_link
from logger import logger
from datetime import datetime
from collections import Counter
from aiogram.utils.markdown import escape_md
from pymongo.mongo_client import MongoClient
from pymongo.mongo_client import MongoClient
from config import (
    PRODUCTION,
    MONGO_URL,
    MONGO_DB,
    STATS_COLLECTION,
    USERS_COLLECTION,
    ERROR_COLLECTION,
)

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB]
stats_collection = mongo_db[STATS_COLLECTION]
users_collection = mongo_db[USERS_COLLECTION]
error_collection = mongo_db[ERROR_COLLECTION]

def feed_stats():
    pipeline = [
        {"$sort": {"date": -1}},
        {
            "$group": {
                "_id": "$link",
                "link": {"$first": "$link"},
                "video_title": {"$first": "$video_title"},
                "date": {"$first": "$date"},
            }
        },
        {"$sort": {"date": -1}},
        {"$limit": 100},
    ]

    sorted_feed = list(stats_collection.aggregate(pipeline))
    filtered_data = list(
        map(
            lambda doc: {
                "link": escape_md(doc["_id"]),
                "video_title": escape_md(doc["video_title"]),
            },
            filter(lambda doc: is_link(doc["_id"]), sorted_feed),
        )
    )

    links_str = "\n".join(
        map(lambda x: f"[{x['video_title']}]({x['link']})", filtered_data[:20])
    )
    return f"{links_str}"


def user_stats():
    users = users_collection.find({})
    usernames = set(
        map(lambda x: json.loads(x["user"]).get("username", "no_user_name"), users)
    )
    sorted_usernames = sorted(usernames)[:100]
    formatted_usernames = "\n".join(map(lambda x: f"``` {x} ```", sorted_usernames))

    return formatted_usernames


def usage_stats():
    usersc = list(map(lambda x: json.loads(x["user"]), users_collection.find({})))
    data = list(
        map(
            lambda user: {
                "username": user.get("username", "no_user_name"),
                "id": user.get("id", -1),
            },
            usersc,
        )
    )

    user_counts = Counter(
        doc["user"] for doc in stats_collection.find() if doc["user"] is not None
    )
    user_counts_sorted = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)

    user_list = [
        {"username": username, "user_id": user_id, "count": count}
        for user_id, count in user_counts_sorted
        if (
            username := next(
                (obj["username"] for obj in data if obj["id"] == user_id), None
            )
        )
    ]

    user_counts_str = "\n".join(
        map(
            lambda x: f"``` {x['count']}\t{x['username']}\t{x['user_id']} ```",
            user_list[:20],
        )
    )

    return user_counts_str


def save_user(user: str):
    user_doc = {"date": datetime.now(), "user": str(user)}
    users_collection.insert_one(user_doc)


def save_stats(chat_id: int, video_url: str, data: str = ""):
    stats_doc = {
        "date": datetime.now(),
        "user": chat_id,
        "link": video_url,
        "video_title": data,
    }

    if not PRODUCTION:
        logger.info(f"save_stats {stats_doc}")
        return
    try:
        stats_collection.insert_one(stats_doc)
    except Exception as e:
        logger.error(f"err stats_collection insert_one to MongoDB {str(e)}")


def save_error(chat_id: int, video_url: str, data: str = ""):
    if not PRODUCTION:
        logger.error(f"error_collection {data}")
        return
    try:
        stats_doc = {
            "date": datetime.now(),
            "user": chat_id,
            "link": video_url,
            "error": data,
        }
        error_collection.insert_one(stats_doc)
    except Exception as e:
        logger.error(f"err stats_collection insert_one to MongoDB {str(e)}")
