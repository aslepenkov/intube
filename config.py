from dotenv import load_dotenv
import os

# Set before start!☜(ﾟヮﾟ☜)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
MONGO_URL = os.getenv("MONGO_URL")
# Set before start!☜(ﾟヮﾟ☜)

STATS_COLLECTION = os.getenv("STATS_COLLECTION")
USERS_COLLECTION = os.getenv("USERS_COLLECTION")
ERROR_COLLECTION = os.getenv("ERROR_COLLECTION")
MONGO_DB = os.getenv("MONGO_DB")

PRODUCTION = os.getenv("PRODUCTION", False)
REPLY_WITH_ERRORS = os.getenv("REPLY_WITH_ERRORS", True)
MAX_DURATION_IN_MINUTES = int(os.getenv("MAX_DURATION_IN_MINUTES", 30))
WORKERS_COUNT = int(os.getenv("WORKERS_COUNT", 2))
SUPPORTED_URLS = [
    "https://twitter.com/",
    "https://instagram.com/",
    "https://www.instagram.com/",
    "https://vt.tiktok.com/",
    "https://vm.tiktok.com/",
    "https://www.tiktok.com/",
    "https://youtu.be/",
    "https://youtube.com/",
    "https://www.youtube.com/",
    "twitter.com/",
    "instagram.com/",
    "youtu.be/",
    "youtube.com/",
    "www.youtube.com/",
]

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
WEBAPP_PORT = os.getenv("PORT", default=8000)
WEBHOOK_HOST = f"https://{HEROKU_APP_NAME}.herokuapp.com"
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"


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


load_dotenv('.env')
