from modules.logger import logger
from modules.bot import dp, on_startup, on_shutdown
from aiogram.utils.executor import start_webhook, start_polling
from modules.config import PRODUCTION, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT

if __name__ == "__main__":
    logger.info("Starting bot")

    if not PRODUCTION:
        # HOME PC RUN
        start_polling(dp, skip_updates=True)
    else:
        # WEBSERVER RUN
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
