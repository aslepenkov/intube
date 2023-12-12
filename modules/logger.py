import logging
import os
import datetime

log_dir_name = "logs"
log_dir = os.path.join(os.getcwd(), log_dir_name)
log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_path = os.path.join(log_dir, log_filename)
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
)

logger = logging.getLogger()


def last_logfile():
    log_files = sorted(os.listdir(log_dir))

    return os.path.join(log_dir, log_files[-1])


def last_logs():
    lines = ""
    latest_log_file = last_logfile()

    # Read the last 25 lines from the latest log file
    with open(latest_log_file, "r") as file:
        lines = file.readlines()[-25:]

    formatted_lines = "\n".join(lines)

    # Format the lines as markdown code
    return f"```\n{formatted_lines}\n```"
