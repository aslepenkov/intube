from dotenv import load_dotenv

load_dotenv(".env")

import asyncio
from modules.logger import logger
from modules.bot import bot_starter

if __name__ == "__main__":
    logger.info("Starting bot")
    asyncio.run(bot_starter())