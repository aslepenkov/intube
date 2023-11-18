from dotenv import load_dotenv
load_dotenv('.env')

from modules.logger import logger
from modules.bot import dp
from aiogram.utils.executor import start_polling

if __name__ == "__main__":
    logger.info("Starting bot")
    start_polling(dp, skip_updates=True)
