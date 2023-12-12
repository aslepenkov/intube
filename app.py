from modules.bot import bot_starter
from modules.logger import logger
import asyncio
from dotenv import load_dotenv

load_dotenv(".env", override=True)


if __name__ == "__main__":
    logger.info("Starting bot")
    asyncio.run(bot_starter())
