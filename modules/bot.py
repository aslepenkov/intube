import os
import asyncio
from aiogram import F
from aiogram import Dispatcher, Bot, types, Router
from aiogram.filters import Command, CommandStart
from modules.core import process_message
from modules.mongo import save_user, feed_stats, usage_stats, user_stats
from modules.logger import last_logs, last_logfile
from modules.config import TOKEN, START_MESSAGE, WAIT_MESSAGE
from modules.config import (
    WORKERS_COUNT,
    ADMIN_USER_ID
)
from modules.utils import admin_required
from aiogram.types import FSInputFile

router = Router(name=__name__)
dp = Dispatcher()

message_queue = asyncio.Queue()
processing_now = asyncio.Queue()


async def bot_starter() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    await bot.send_message(ADMIN_USER_ID, "intube alive")
    # And the run events dispatching
    await dp.start_polling(bot)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply(START_MESSAGE)
    save_user(message.from_user)

# show available actions for user with ADMIN_USER_ID
@dp.message(Command("admin"))
@admin_required
async def feed(message: types.Message):
    msg = "/feed\n/usage\n/users\n/log\n/logfile"
    await message.reply(msg)

# show last downloaded links
@dp.message(Command("feed"))
@admin_required
async def feed(message: types.Message):
    stats = feed_stats()
    await message.reply(stats, parse_mode="MarkdownV2")


# show stats: video_downloaded - user - user id
@dp.message(Command("usage"))
@admin_required
async def admin(message: types.Message):
    stats = usage_stats()
    await message.reply(stats, parse_mode="MarkdownV2")


# show usernames
@dp.message(Command("users"))
@admin_required
async def admin(message: types.Message):
    stats = user_stats()
    await message.reply(stats, parse_mode="MarkdownV2")


# show logfile last lines
@dp.message(Command("log"))
@admin_required
async def log(message: types.Message):
    formatted_lines = last_logs()
    await message.reply(formatted_lines, parse_mode="MarkdownV2")


@dp.message(Command("logfile"))
@admin_required
async def log(message: types.Message):
    logfile = last_logfile()
    await message.reply_document(FSInputFile(logfile))


# handle all text messages
@dp.message()
@router.message(F.content_type.in_({'text'}))
async def handle_message(message: types.Message):
    await message_queue.put(message)

    if processing_now.qsize() < WORKERS_COUNT:
        while not message_queue.empty():
            msg = await message_queue.get()

            await processing_now.put(msg)
            await process_message(msg)
            await processing_now.get()
    else:
        queue_size = message_queue.qsize() + WORKERS_COUNT
        await message.reply(WAIT_MESSAGE.format(queue_size))
