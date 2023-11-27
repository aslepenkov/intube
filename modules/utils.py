import os
import re
from pathlib import Path
from pathlib import Path
from aiogram import types
from functools import wraps
from modules.config import ADMIN_USER_ID


async def reply_text(message: types.Message, message_text: str):
    await message.reply(message_text)


async def reply_video(message: types.Message, video_file: str, delete: bool = True):
    with open(video_file, "rb") as video:
        await message.reply_video(video)

    if delete:
        remove_file_safe(video_file)


async def reply_photo(message: types.Message, file: str, delete: bool = True):
    with open(file, "rb") as photo:
        await message.reply_photo(photo)

    if delete:
        remove_file_safe(file)


async def reply_audio(message: types.Message, audio_file: str):
    with open(audio_file, "rb") as audio:
        await message.reply_audio(audio)

    remove_file_safe(audio_file)


async def reply_voice(message: types.Message, audio_file: str, title: str):
    with open(audio_file, "rb") as audio:
        await message.reply(title)
        await message.reply_voice(audio)

    remove_file_safe(audio_file)


async def reply_file(message: types.Message, file: str):
    with open(file, "rb") as f:
        await message.reply_document(f)

    remove_file_safe(file)


def remove_file_safe(file: str):
    if Path(file).is_file():
        os.remove(file)


def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / 1024 / 1024


def is_link(string):
    pattern = r"^(http|https)://[^\s/$.?#].[^\s]*$"
    return re.match(pattern, string) is not None


def admin_required(func):
    @wraps(func)
    async def wrapper(message: types.Message):
        user_id = message.from_user.id

        if user_id != int(ADMIN_USER_ID):
            await message.reply(f"(╯°□°）╯︵ ┻━┻")
            return

        return await func(message)

    return wrapper
