import os
import re
from pathlib import Path
from pathlib import Path
from aiogram import types


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
