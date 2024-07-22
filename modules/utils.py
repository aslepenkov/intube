import os
import re
from PIL import Image
from pathlib import Path
from aiogram import types
from functools import wraps
from aiogram.types import FSInputFile
from modules.config import (
    MONGO_URL, ADMIN_USER_ID
)

async def reply_text(message: types.Message, message_text: str):
    await message.reply(message_text)


async def reply_video(message: types.Message, video_file_path: str, height: int, width: int):
    if Path(video_file_path).is_file():
        await message.reply_video(FSInputFile(f'{video_file_path}'),
                                  height=height,
                                  width=width)


async def reply_photo(message: types.Message, file: str):
    await message.reply_photo(FSInputFile(file))


async def reply_audio(message: types.Message, audio_file: str, title: str, media_duration: int):
    thumbnail_filename = f'{audio_file}.jpg'
    media_filename = f'{audio_file}.webp'
    if Path(file).is_file():
        thumbnail = Image.open(media_filename).convert(
            'RGB').resize((840, 480))
        thumbnail.save(thumbnail_filename, 'jpeg')

    if Path(audio_file).is_file() and Path(thumbnail_filename).is_file():
        await message.reply_audio(
            audio=FSInputFile(audio_file),
            caption=title,
            duration=media_duration,
            title=title,
            thumbnail=FSInputFile(thumbnail_filename),
            performer='@intube_bot'
        )


# deprecated
async def reply_voice(message: types.Message, audio_file: str, title: str):
    await message.reply(title)
    await message.reply_voice(FSInputFile(audio_file))


async def reply_file(message: types.Message, file: str):
    await message.reply_document(FSInputFile(file))


def remove_file_safe(file: str):
    if Path(file).is_file():
        os.remove(file)


def remove_files_containing(temp_dir: str, file_substr: str):
    for filename in os.listdir(temp_dir):
        if file_substr in filename:
            file_path = os.path.join(temp_dir, filename)
            if Path(file_path).is_file():
                os.remove(file_path)


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


def mongo_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not MONGO_URL:
            return

        return func(*args, **kwargs)

    return wrapper


def escape_md(text):
    special_chars = '\\`*_{}[]()#+-.!=|'
    escaped = ''.join(
        ['\\' + char if char in special_chars else char for char in text])
    return escaped


def extract_first_url(message):
    # Regular expression pattern to match a URL
    url_pattern = r'(https?://\S+)'

    # Search for the first match in the message
    match = re.search(url_pattern, message)

    if match:
        return match.group(1)  # Return the first URL found
    else:
        return None

def remove_extension(file_name: str) -> str:
    return file_name.rsplit('.', 1)[0]