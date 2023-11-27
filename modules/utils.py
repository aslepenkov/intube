import os
import re
from pathlib import Path
from pathlib import Path
from aiogram import types
from functools import wraps
from modules.config import ADMIN_USER_ID
from aiogram.types import FSInputFile

async def reply_text(message: types.Message, message_text: str):
    await message.reply(message_text)


async def reply_video_new(message: types.Message, video_file: str, delete: bool = True):
    await message.reply_video(FSInputFile(video_file))

    if delete:
        remove_file_safe(video_file)


async def reply_photo(message: types.Message, file: str, delete: bool = True):
    await message.reply_photo(FSInputFile(file))

    if delete:
        remove_file_safe(file)


async def reply_audio(message: types.Message, audio_file: str):
    await message.reply_audio(FSInputFile(audio_file))

    remove_file_safe(audio_file)


async def reply_voice(message: types.Message, audio_file: str, title: str):
    await message.reply(title)
    await message.reply_voice(FSInputFile(audio_file))

    remove_file_safe(audio_file)


async def reply_file(message: types.Message, file: str):
    await message.reply_document (FSInputFile(file))

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

def escape_m1d(text: str) -> str:
    """
    Escapes markdown-sensitive characters within other markdown
    constructs.
    """
    return re.compile(r"([\\\[\]\(\)])").sub(r"\\\1", text)

def escape_md(txt) -> str:
  match_md = r'((([\.\#\(\)_*!]).+?\3[\.\#\(\)^_*!]*)*)([\.\#\(\)_*!])'
  return re.sub(match_md, "\g<1>\\\\\g<4>", txt)