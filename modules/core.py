import os
import uuid
import yt_dlp
from aiogram import types
from modules.logger import logger
from modules.mongo import save_error, save_stats
from modules.utils import (
    reply_video,
    reply_audio,
    reply_text,
    remove_file_safe,
    extract_first_url,
    remove_extension,
)
from modules.config import DOWNLOAD_STARTED, EX_VALID_LINK, TEMP_DIR
from yt_dlp.utils import DateRange
import json
import subprocess

class DownloadedMedia:
    def __init__(
        self,
        file_name="",
        title="untitled",
        is_audio=False,
        duration=0,
        height=0,
        width=0,
    ):
        self.file_name = file_name
        self.title = title
        self.is_audio = is_audio
        self.duration = duration
        self.height = height
        self.width = width

    def to_json(self):
        return json.dumps(self.__dict__)


async def process_message(message: types.Message):
    force_audio = "/audio" in message.text
    url = extract_first_url(message.text)
    is_group_chat = message.chat.type in ["group", "supergroup"]
    if not url and not is_group_chat:
        await message.reply(EX_VALID_LINK)
        return
    try:
        media = None
        media_title = None
        file_path = None

        await message.reply(DOWNLOAD_STARTED)
        if "instagram" in url:
            url = url.replace("instagram.com", "ddinstagram.com")
            await reply_text(message, url)
        else:
            media = await download_media(url, message, force_audio)

            is_audio = media.is_audio
            file_path = media.file_name
            media_title = media.title
            media_duration = media.duration
            media_height = media.height
            media_width = media.width

            if is_audio:
                await reply_audio(message, file_path, media_title, media_duration)
            else:
                await reply_video(message, file_path, media_height, media_width)
    except Exception as e:
        if not is_group_chat:
            await message.reply(f"Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))
    finally:
        if file_path:
            remove_file_safe(file_path)
        if media:
            save_stats(message.from_user.id, url, media.title)


async def download_media(url: str, message, force_audio: bool = False):
    temp_file_name = str(uuid.uuid4())
    temp_file = os.path.join(TEMP_DIR, temp_file_name)
    os.makedirs(TEMP_DIR, exist_ok=True)

    ydl_opts_shorts = {
        "outtmpl": f"{temp_file}",
        #"format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        #"format": "bestvideo[ext=mp4]+bestaudio/best",
        "noplaylist": True,
        "writethumbnail": True,
    }

    ydl_opts_video = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "outtmpl": f"{temp_file}",
        "noplaylist": True,
        "writethumbnail": True,
    }

    ydl_opts_audio = {
        "format": "bestaudio[filesize_approx<=50M]/bestaudio[filesize<=50M]",
        "outtmpl": f"{temp_file}",
        "noplaylist": True,
        "writethumbnail": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_video, yt_dlp.YoutubeDL(
        ydl_opts_audio
    ) as ydl_audio, yt_dlp.YoutubeDL(ydl_opts_shorts) as ydl_short:
        info = ydl_video.extract_info(url, download=False)
        info_audio = ydl_audio.extract_info(url, download=False)

        duration = info.get("duration", 0)
        width = info.get("width", 0)
        height = info.get("height", 0)

        # Determine if the video is a YouTube Short
        is_short = duration < 60 and width < height

        if force_audio or (duration / 60) > 10:
            duration = info_audio.get("duration", 0)
            ydl_audio.download([url])
            is_audio = True
            temp_file = remove_extension(temp_file)
        elif is_short:
            ydl_short.download([url])
            is_audio = False
            temp_file = f"{temp_file}.mp4"
            subprocess.run([
                "ffmpeg", "-i", temp_file,
                "-c:v", "libx264", "-c:a", "aac",
                "-strict", "experimental", f"coded_{temp_file}"
            ])
            return DownloadedMedia(f"coded_{temp_file}", info.get("title", "untitled"), False, duration)
        else:
            ydl_video.download([url])
            is_audio = False
            temp_file = f"{temp_file}.mp4"

    return DownloadedMedia(f"{temp_file}", info.get("title", "untitled"), is_audio, duration)
