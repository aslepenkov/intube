import os
import uuid
import yt_dlp
from aiogram import types
from modules.logger import logger
from modules.mongo import save_error, save_stats
from modules.utils import reply_video, reply_audio, reply_text, remove_file_safe
from modules.config import (
    DOWNLOAD_STARTED,
    SUPPORTED_URLS,
    MAX_SIZE_IN_MBYTES,
    EX_VALID_LINK,
    EX_MAX_DURATION,
)


async def process_message(message: types.Message):
    url = message.text

    if not any(url.startswith(prefix) for prefix in SUPPORTED_URLS):
        await message.reply(EX_VALID_LINK)
        return

    try:
        media = None
        media_title = None
        await message.reply(DOWNLOAD_STARTED)
        if "instagram" in url:
            url = url.replace("instagram.com", "ddinstagram.com")
            await reply_text(message, url)
        else:
            media = await download_media(url)

            if not media:
                await reply_text(message, "oops ᓚᘏᗢ")

            temp_file = media[0]
            media_title = media[1]
            is_audio = media[2]
            media_duration = media[3]

            if is_audio:
                await reply_audio(message, temp_file, media_title, media_duration)
            else:
                await reply_video(message, temp_file)
    except Exception as e:
        await message.reply(f"Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))
    finally:
        media = media_title if media else ""
        remove_file_safe(temp_file)
        save_stats(message.from_user.id, url, media)


async def download_media(url: str):
    temp_dir = "temp"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}.mp4"
    os.makedirs(temp_dir, exist_ok=True)
    video_title = "untitled"

    ydl_opts = {
        "outtmpl": temp_file,
        "noplaylist": True,
        "format": "best[filesize<=50M]/w[ext=mp4]/w[ext=m4a]/w[ext=webm]/wa"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Only fetch metadata
        duration = info.get("duration", 0)
        video_title = info.get("title", "untitled")

        if duration / 60 < 15:
            ydl.download([url])
        else:
            return await download_audio(url)

    return [temp_file, video_title, False, duration]


async def download_audio(url: str):
    is_audio = True
    temp_dir = "temp"
    media_title = "untitled"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}.mp3"

    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": temp_file,
        "noplaylist": True,
        "format": "wa",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Only fetch metadata
        media_title = info.get("title", "untitled")
        filesize = info.get("filesize", 0) / 1024 / 1024  # MBytes
        duration = int(info.get("duration", 0))

        if filesize <= MAX_SIZE_IN_MBYTES:
            ydl.download([url])
        else:
            raise Exception(EX_MAX_DURATION.format(MAX_SIZE_IN_MBYTES))

    return [temp_file, media_title, is_audio, duration]
