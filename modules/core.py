import os
import uuid
import yt_dlp
from aiogram import types
from modules.logger import logger
from modules.mongo import save_error, save_stats
from modules.utils import reply_video, reply_audio, reply_text, remove_files_containing, extract_first_url
from modules.config import (
    DOWNLOAD_STARTED,
    SUPPORTED_URLS,
    EX_VALID_LINK,
    TEMP_DIR
)


class DownloadedMedia:
    def __init__(self, file_name="", title="untitled", is_audio=False, duration=0):
        self.file_name = file_name
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

            is_audio = media.is_audio
            file_name = media.file_name
            media_title = media.title
            media_duration = media.duration

            temp_file = os.path.join(TEMP_DIR, file_name)

            if is_audio:
                await reply_audio(message, temp_file, media_title, media_duration)
            else:
                await reply_video(message, temp_file)

    except Exception as e:
        await message.reply(f"Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))

    finally:
        media = media_title if media else ""
        if file_name:
            remove_files_containing(TEMP_DIR, file_name)
        save_stats(message.from_user.id, url, media)


async def download_media(url: str):
    temp_file_name = str(uuid.uuid4())
    temp_file = os.path.join(TEMP_DIR, temp_file_name)
    os.makedirs(TEMP_DIR, exist_ok=True)
    is_audio = False

    ydl_opts_video = {
        "outtmpl": f"{temp_file}.mp4",
        "noplaylist": True,
        "format": "best[filesize<=50M]",
        'writethumbnail': True,
    }

    ydl_opts_audio = {
        "outtmpl": f"{temp_file}",
        "noplaylist": True,
        "format": "bestaudio[filesize<=50M][ext=mp3]/bestaudio[filesize<=50M][ext=m4a]",
        'writethumbnail': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_video, yt_dlp.YoutubeDL(ydl_opts_audio) as ydl_audio:
        info = ydl_video.extract_info(
            url, download=False)  # Only fetch metadata
        info_a = ydl_audio.extract_info(
            url, download=False)  # Only fetch metadata

        duration = info.get("duration", 0)
        duration_a = info_a.get("duration", 0)

        if duration / 60 < 15:
            ydl_video.download([url])
            is_audio = False
            file_name = f"{temp_file_name}.mp4"
        else:
            ydl_audio.download([url])
            is_audio = True
            file_name = f"{temp_file_name}"
            duration = duration_a

    return DownloadedMedia(file_name, info.get("title", "untitled"), is_audio, duration)
