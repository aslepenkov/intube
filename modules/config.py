from dotenv import load_dotenv
import os

PRODUCTION = eval(os.getenv("PRODUCTION", False))

if not PRODUCTION:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_DEBUG") 
else:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_PROD") 

ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
MONGO_URL = os.getenv("MONGO_URL")

STATS_COLLECTION = os.getenv("STATS_COLLECTION")
USERS_COLLECTION = os.getenv("USERS_COLLECTION")
ERROR_COLLECTION = os.getenv("ERROR_COLLECTION")
MONGO_DB = os.getenv("MONGO_DB")

MAX_DURATION_IN_MINUTES = int(os.getenv("MAX_DURATION_IN_MINUTES", 30))
WORKERS_COUNT = int(os.getenv("WORKERS_COUNT", 2))
SUPPORTED_URLS = [
    "https://twitter.com/",
    "https://instagram.com/",
    "https://www.instagram.com/",
    "https://ddinstagram.com/",
    "https://vt.tiktok.com/",
    "https://vm.tiktok.com/",
    "https://www.tiktok.com/",
    "https://youtu.be/",
    "https://youtube.com/",
    "https://www.youtube.com/",
    "https://m.youtube.com/",
    "twitter.com/",
    "instagram.com/",
    "ddinstagram.com/",
    "youtu.be/",
    "youtube.com/",
    "www.youtube.com/",
    "m.youtube.com/",
]

# Messages
INSTAGRAM_NOT_SUPPORTED_MESSAGE = (
    f"Right now Instagram is not supported, stay tuned ¯\_(ツ)_/¯"
)
START_MESSAGE = f"Hi! Send me a link. I can download instagram reels, youtube shorts, twitter & tiktok videos ╰(*°▽°*)╯ "
DOWNLOAD_STARTED = "(☞ﾟヮﾟ)☞ Download Started..."
WAIT_MESSAGE = "You are number {} in the queue. Please wait a bit ಠ_ಠ"
EX_MAX_DURATION = "I can't download videos longer than {} minutes ಥ_ಥ "
EX_VALID_LINK = """
I need a valid link ༼ つ ◕_◕ ༽つ
Example: 
https:/www.instagram.com/reel/*
https:/www.youtube.com/shorts/*
https:/vt.tiktok.com/*
https:/twitter.com/*/status/*
"""

