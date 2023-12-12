import json
from modules.utils import is_link
from modules.logger import logger
from datetime import datetime
from collections import Counter
from pymongo.mongo_client import MongoClient
from modules.utils import escape_md
from modules.config import (
    MONGO_URL,
    MONGO_DB,
    STATS_COLLECTION,
    USERS_COLLECTION,
    ERROR_COLLECTION,
)
from aiogram import types
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
        {"$match": {"video_title": {"$exists": True, "$ne": ""}}},
        {"$sort": {"date": -1}},
        {"$limit": 200},
    ]

    sorted_feed = list(stats_collection.aggregate(pipeline))
    filtered_data = list(
        map(
            lambda doc: {
                "link": escape_md(doc["link"]),
                "video_title": escape_md(doc["video_title"]),
            },
            sorted_feed
        )
    )

    links_str = "\n".join(
        map(lambda x: f"[{x['video_title']}]({x['link']})", filtered_data[:30])
    )

    return f"{links_str}"


def user_stats():
    # Aggregation pipeline to handle usernames and IDs
    pipeline = [
        {
            '$project': {
                'username': {
                    '$cond': {
                        'if': {'$ne': ['$userObj.username', None]},
                        'then': '$userObj.username',
                        'else': {'$toString': '$userObj.id'}
                    }
                }
            }
        },
        {
            '$addFields': {
                'lowercase_username': {'$toLower': '$username'}
            }
        },
        {
            # Sort by lowercase username in ascending order (-1 for descending)
            '$sort': {'lowercase_username': 1}
        },
        {
            '$project': {
                'lowercase_username': 1,  # Include the original username field
            }
        }
    ]
    # Perform the aggregation
    result = list(users_collection.aggregate(pipeline))

    # Extract usernames from the aggregation result
    usernames = [entry['lowercase_username'] for entry in result]

    # Format and return the unique usernames
    # Get the first 100 unique usernames
    formatted_usernames = "\n".join(usernames[:150])
    return f"```\n{formatted_usernames}\n```"


def usage_stats():
    total_stats_documents = stats_collection.count_documents({})
    pipeline = [
        {
            '$lookup': {
                'from': f'{stats_collection.name}',
                'localField': 'userObj.id',
                'foreignField': 'user',
                'as': 'user_stats'
            }
        },
        {
            '$match': {
                # Filter out documents with empty 'user_stats' array
                'user_stats': {'$ne': []}
            }
        },
        {
            '$project': {
                'username': {'$ifNull': ['$userObj.username', {'$toString': '$userObj.id'}]},
                'statsCount': {'$size': '$user_stats'}
            }
        },
        {
            '$group': {
                '_id': '$username',
                'totalStatsCount': {'$sum': '$statsCount'}
            }
        },
        {
            # Sort by totalStatsCount in descending order
            '$sort': {'totalStatsCount': -1}
        }
    ]

    # Perform the aggregation
    result = list(users_collection.aggregate(pipeline))[:150]

    # Sort the usernames in descending order by totalStatsCount and format as markdown pre
    formatted_usernames = "\n".join(
        [f"{entry['_id']}: {entry['totalStatsCount']}" for entry in result])

    return f"```\n{formatted_usernames}\n```\nTotal usage: {total_stats_documents}"


def save_user(user):
    existing_user = users_collection.find_one({"userObj.id": user.id})

    if existing_user:
        return

    user_doc = {"date": datetime.now(), "userObj": dict(user)}
    users_collection.insert_one(user_doc)


def save_stats(chat_id: int, video_url: str, data: str = ""):
    stats_doc = {
        "date": datetime.now(),
        "user": chat_id,
        "link": video_url,
        "video_title": data,
    }

    try:
        stats_collection.insert_one(stats_doc)
        logger.info(f"stats_collection {stats_doc}")
    except Exception as e:
        logger.error(f"error_collection insert_one to MongoDB {str(e)}")


def save_error(chat_id: int, video_url: str, data: str = ""):
    try:
        error_doc = {
            "date": datetime.now(),
            "user": chat_id,
            "link": video_url,
            "error": data,
        }
        logger.error(f"error_collection {error_doc}")
        error_collection.insert_one(error_doc)
    except Exception as e:
        logger.error(f"error_collection insert_one to MongoDB {str(e)}")
