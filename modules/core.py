import os
import uuid
import yt_dlp
from aiogram import types
from modules.logger import logger
from modules.mongo import save_error, save_stats
from modules.utils import reply_video, reply_audio, reply_text, remove_file_safe, extract_first_url
from modules.config import (
    DOWNLOAD_STARTED,
    SUPPORTED_URLS,
    MAX_SIZE_IN_MBYTES,
    EX_VALID_LINK,
    EX_MAX_DURATION,
)


class DownloadedMedia:
    def __init__(self, file_path="", title="untitled", is_audio=False, duration=0):
        self.file_path = file_path
        self.title = title
        self.is_audio = is_audio
        self.duration = duration


async def process_message(message: types.Message):
    url = extract_first_url(message.text)

    if not any(url.startswith(prefix) for prefix in SUPPORTED_URLS):
        await message.reply(EX_VALID_LINK)
        return

    try:
        media = None
        media_title = None
        temp_file = None

        await message.reply(DOWNLOAD_STARTED)
        if "instagram" in url:
            url = url.replace("instagram.com", "ddinstagram.com")
            await reply_text(message, url)
        else:
            media = await download_media(url)

            temp_file = media.file_path
            media_title = media.title
            is_audio = media.is_audio
            media_duration = media.duration

            if is_audio:
                await reply_audio(message, temp_file, media_title, media_duration)
            else:
                await reply_video(message, temp_file)

    except Exception as e:
        await message.reply(f"Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))

    finally:
        media = media_title if media else ""
        if temp_file:
            remove_file_safe(temp_file)
        save_stats(message.from_user.id, url, media)


async def download_media(url: str):
    temp_dir = "temp"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}"
    os.makedirs(temp_dir, exist_ok=True)
    is_audio = False

    ydl_opts_video = {
        "outtmpl": f"{temp_file}.mp4",
        "noplaylist": True,
        "format": "best[filesize<=50M]"
    }

    ydl_opts_audio = {
        "outtmpl": f"{temp_file}.mp3",
        "noplaylist": True,
        "format": "bestaudio[filesize<=50M]/w"
    }

    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_video, yt_dlp.YoutubeDL(ydl_opts_audio) as ydl_audio:
        info = ydl_video.extract_info(
            url, download=False)  # Only fetch metadata
        info_a = ydl_audio.extract_info(
            url, download=False)  # Only fetch metadata
        duration = info.get("duration", 0)

        if duration / 60 < 15:
            ydl_video.download([url])
            is_audio = False
            file_path = f"{temp_file}.mp4"
        else:
            ydl_audio.download([url])
            is_audio = True
            file_path = f"{temp_file}.mp3"

    return DownloadedMedia(file_path, info.get("title", "untitled"), is_audio, duration)