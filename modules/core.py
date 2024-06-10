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
    EX_VALID_LINK,
    TEMP_DIR
)
from yt_dlp.utils import DateRange
import json


class DownloadedMedia:
    def __init__(self, file_name="", title="untitled", is_audio=False, duration=0, height=0, width=0):
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

    if not url or not any(url.startswith(prefix) for prefix in SUPPORTED_URLS):
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
            media = await download_media(url, force_audio)

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
        await message.reply(f"Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))

    finally:
        if file_path:
            remove_file_safe(file_path)

        if media:
            save_stats(message.from_user.id, url, media.title)


async def download_media(url: str, force_audio: bool = False):

    temp_file_name = str(uuid.uuid4())
    temp_file = os.path.join(TEMP_DIR, temp_file_name)
    os.makedirs(TEMP_DIR, exist_ok=True)

    ydl_opts_video = {
        "outtmpl": f"{temp_file}.mp4",
        "noplaylist": True,
        "format": "best[filesize_approx<=50M][ext=mp4]/best[filesize<=50M][ext=mp4]/best[filesize_approx<=50M]/best[filesize<=50M]/wa",
        'writethumbnail': True,
    }

    ydl_opts_audio = {
        "outtmpl": f"{temp_file}",
        "noplaylist": True,
        "format": "bestaudio[filesize_approx<=50M][ext=m4a]/bestaudio[filesize<=50M][ext=m4a]/wa",
        'writethumbnail': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_video, yt_dlp.YoutubeDL(ydl_opts_audio) as ydl_audio:
        info = ydl_video.extract_info(
            url, download=False)
        info_audio = ydl_audio.extract_info(
            url, download=False)

        duration = info.get("duration", 0)

        if force_audio or (duration / 60) > 15:
            duration = info_audio.get("duration", 0)
            ydl_audio.download([url])
            is_audio = True
        else:
            ydl_video.download([url])
            is_audio = False
            temp_file = f"{temp_file}.mp4"
            

    return DownloadedMedia(temp_file, info.get("title", "untitled"), is_audio, duration)


async def get_videos(message: types.Message):
    # return
    history_start = '20231201'
    history_end = '20231231'

    link = message.text
    response = ""
    ydl_opts = {
        'quiet': False,
        'daterange': DateRange(history_start, history_end),
        'skip_download': True,
        'playlist_end': 10  # Set playlist_end to limit fetched items
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)

            if 'entries' in info:
                videos = info['entries'][:10]
                response += f"Videos from {info['uploader']}:\n\n"
                for video in videos:
                    title = video['title']
                    url = video['webpage_url']
                    response += f"[{title}]({url})\n"
                    response += "\n"
            else:
                response += f"No videos found for {link}.\n\n"

        if response:
            await message.reply(response, parse_mode='Markdown')

    except Exception as e:
        await message.reply("Sorry, something went wrong. Please try again later.")
