import os
import uuid
import yt_dlp
import shutil
import instaloader
from modules.logger import logger
from aiogram import types
from modules.mongo import save_error, save_stats
from modules.utils import reply_video, reply_photo
from modules.config import (
    SUPPORTED_URLS,
    DOWNLOAD_STARTED,
    EX_VALID_LINK,
    INSTAGRAM_NOT_SUPPORTED_MESSAGE,
    MAX_DURATION_IN_MINUTES,
    EX_MAX_DURATION,
)


async def process_message(message: types.Message):
    url = message.text

    if not any(url.startswith(prefix) for prefix in SUPPORTED_URLS):
        await message.reply(EX_VALID_LINK)
        return

    try:
        await message.reply(DOWNLOAD_STARTED)

        if "instagram.com/" in url:
            file = await download_and_send_instagram(message, url)
        else:
            file = await download_video(url)
            await reply_video(message, file[0])
        save_stats(message.from_user.id, url, file[1])
    except Exception as e:
        await message.reply(f"Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))


async def download_and_send_instagram(message: types.Message, url: str):
    temp_folder_name = str(uuid.uuid4())
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
        # loader.download_pictures = False
        loader.download_post(post, target=temp_folder_name)

        for filename in os.listdir(temp_folder_name):
            file = os.path.join(temp_folder_name, filename)
            if os.path.isfile(file) and file.lower().endswith("mp4"):
                await reply_video(message, file, False)
            if os.path.isfile(file) and file.lower().endswith("jpg"):
                await reply_photo(message, file, False)
    except Exception as e:
        save_error(message.from_user.id, url, str(e))
        raise Exception(INSTAGRAM_NOT_SUPPORTED_MESSAGE)

    shutil.rmtree(temp_folder_name, ignore_errors=False, onerror=None)

    return [temp_folder_name, url]


async def download_video(url: str):
    temp_dir = "temp"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}.mp4"
    os.makedirs(temp_dir, exist_ok=True)
    video_title = "untitled"

    ydl_opts = {
        "outtmpl": temp_file,
        "format": "best[filesize<=50M][ext=mp4]/w[ext=mp4]",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Only fetch metadata
        duration = info.get("duration", 0)
        video_title = info.get("title", "untitled")

        if duration / 60 < MAX_DURATION_IN_MINUTES:
            ydl.download([url])
        else:
            raise Exception(EX_MAX_DURATION.format(MAX_DURATION_IN_MINUTES))

    return [temp_file, video_title]


async def download_audio(url: str):
    temp_dir = "temp"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}.mp3"
    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": f"{temp_dir}/{temp_file_name}.mp3",
        "format": "bestaudio[ext=mp3]",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Only fetch metadata
        duration = info.get("duration", 0)
        audio_title = info.get("title", "untitled")

        if duration / 60 < MAX_DURATION_IN_MINUTES:
            ydl.download([url])
            audio_file = f"{temp_dir}/{audio_title}.mp3".replace(" ", "_")
            os.rename(temp_file, audio_file)
        else:
            raise Exception(EX_MAX_DURATION.format(MAX_DURATION_IN_MINUTES))

    return audio_file
