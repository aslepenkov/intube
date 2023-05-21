import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Command
from modules.core import process_message
from modules.mongo import save_user, feed_stats, usage_stats, user_stats
from config import TOKEN, START_MESSAGE, WAIT_MESSAGE
from config import (
    WORKERS_COUNT,
    WEBHOOK_URL,
    ADMIN_USER_ID,
)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

message_queue = asyncio.Queue()
processing_now = asyncio.Queue()


@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.reply(START_MESSAGE)
    save_user(message.from_user)


# show last downloaded links
@dp.message_handler(Command("feed"))
async def feed(message: types.Message):
    user_id = message.chat.id

    if user_id != int(ADMIN_USER_ID):
        await message.reply(f"(╯°□°）╯︵ ┻━┻")
        return
    stats = feed_stats()
    await message.reply(stats, parse_mode="MarkdownV2")


# show stats: video_downloaded - user - user id
@dp.message_handler(Command("admin"))
async def admin(message: types.Message):
    user_id = message.chat.id

    if user_id != int(ADMIN_USER_ID):
        await message.reply(f"(╯°□°）╯︵ ┻━┻")
        return
    stats = usage_stats()
    await message.reply(stats, parse_mode="MarkdownV2")


# show usernames
@dp.message_handler(Command("users"))
async def admin(message: types.Message):
    user_id = message.chat.id

    if user_id != int(ADMIN_USER_ID):
        await message.reply(f"(╯°□°）╯︵ ┻━┻")
        return

    stats = user_stats()
    await message.reply(stats, parse_mode="MarkdownV2")


# handle all text messages
@dp.message_handler(content_types=types.ContentType.TEXT)
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


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    if ADMIN_USER_ID:
        await bot.send_message(
            f"{ADMIN_USER_ID}",
            f"(●'◡'●) GIMME COOKIE!",
        )


async def on_shutdown(dispatcher):
    if ADMIN_USER_ID:
        await bot.send_message(
            f"{ADMIN_USER_ID}",
            f"(._.`) on_shutdown message_queue: {message_queue} processing_now: {processing_now}",
        )
    await bot.delete_webhook()
