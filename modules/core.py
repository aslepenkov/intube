import os
import uuid
import yt_dlp
import shutil
import instaloader
from modules.logger import logger
from aiogram import types
from modules.mongo import save_error, save_stats
from modules.utils import reply_video, reply_voice, reply_photo, reply_text
from modules.config import (
    SUPPORTED_URLS,
    DOWNLOAD_STARTED,
    EX_VALID_LINK,
    INSTAGRAM_NOT_SUPPORTED_MESSAGE,
    MAX_SIZE_IN_MBYTES,
    EX_MAX_DURATION,
)


async def process_message(message: types.Message):
    url = message.text

    if not any(url.startswith(prefix) for prefix in SUPPORTED_URLS):
        await message.reply(EX_VALID_LINK)
        return

    try:
        file = None
        await message.reply(DOWNLOAD_STARTED)
        if "instagram.com/" in url:
            # file = await download_and_send_instagram(message, url)
            url = url.replace("instagram.com", "ddinstagram.com")
            url = url.replace("www.", "")
            await reply_text(message, url)
        else:
            file = await download_video(url)
            if file:
                temp_file = file[0]
                media_title = file[1]
                is_audio = file[2]
                if is_audio:
                    await reply_voice(message, temp_file, media_title)
                else:
                    await reply_video(message, temp_file)
                #save_stats(message.from_user.id, url, a_media_title)
    except Exception as e:
        await message.reply(f"[v1] Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))
    finally:
        media = media_title if file else ""
        save_stats(message.from_user.id, url, media)


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

    return [temp_folder_name, url, False]


async def download_video(url: str):
    is_audio = False
    temp_dir = "temp"
    media_title = "untitled"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}.mp4"

    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": temp_file,
        "format": "best[filesize<=50M][ext=webp]/w[ext=mp4]",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Only fetch metadata
        duration = 
        
        
        
        
        
        
        
        
        
        int(info.get("duration", 0))
        filesize = int( info.get("filesize", 0))
        media_title = info.get("title", "untitled")


        if duration > 15 * 60 or filesize > MAX_SIZE_IN_MBYTES *1024*1024:
            is_audio = True
            temp_file = f"{temp_dir}/{temp_file_name}.mp3"
            ydl_audio_opts = {
                "outtmpl": temp_file,
                "format": "wa",  # "bestaudio[ext=mp3]"
            }
            with yt_dlp.YoutubeDL(ydl_audio_opts) as ydla:
                info = ydla.extract_info(url, download=False)  # Only fetch metadata
                filesize = info.get("filesize", 0) / 1024 / 1024  # MBytes
                media_title = info.get("title", "untitled")
                
                if filesize <= MAX_SIZE_IN_MBYTES:
                    ydla.download([url])
                else:
                    raise Exception(EX_MAX_DURATION.format(MAX_SIZE_IN_MBYTES))
        else:
            ydl.download([url])

    return [temp_file, media_title, is_audio]


async def download_video_chatgpt_refactored(url: str):
    is_audio = False
    temp_dir = "temp"
    media_title = "untitled"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}"

    os.makedirs(temp_dir, exist_ok=True)

    def download_media(ydl_opts, file_extension):
        nonlocal temp_file, media_title, is_audio
        temp_file_with_ext = f"{temp_file}.{file_extension}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filesize = info.get("filesize", 0) 

            if filesize:
                filesize = filesize / 1024 / 1024  # MBytes  
            else: 
                filesize = 0

            media_title = info.get("title", "untitled")

            if filesize <= MAX_SIZE_IN_MBYTES:
                ydl.download(url)
            else:
                raise Exception(f"File size exceeds {MAX_SIZE_IN_MBYTES} MB")

        temp_file = temp_file_with_ext
        is_audio = file_extension == "mp3"

    video_opts = {
        "outtmpl": temp_file + ".mp4",
        "format": "best[filesize<=50M][ext=mp4]/w[ext=mp4]",
    }
    audio_opts = {
        "outtmpl": temp_file + ".mp3",
        "format": "wa",  # "bestaudio[ext=mp3]"
    }

    download_media(video_opts, "mp4")

    if is_audio:
        download_media(audio_opts, "mp3")

    return [temp_file, media_title, is_audio]
