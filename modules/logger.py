import logging
import os
import datetime

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_path = os.path.join(log_dir, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_path)]
)

logger = logging.getLogger()