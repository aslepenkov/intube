import os
import uuid
import yt_dlp
import shutil
import instaloader
from modules.logger import logger
from aiogram import types
from modules.mongo import save_error, save_stats
from modules.utils import reply_video_new, reply_voice, reply_photo, reply_text
from modules.config import (
    SUPPORTED_URLS,
    DOWNLOAD_STARTED,
    EX_VALID_LINK,
    MAX_SIZE_IN_MBYTES,
    EX_MAX_DURATION,
)
import copy

async def process_message(message: types.Message):
    url = message.text

    if not any(url.startswith(prefix) for prefix in SUPPORTED_URLS):
        await message.reply(EX_VALID_LINK)
        return

    try:
        file = None
        media_title = None
        await message.reply(DOWNLOAD_STARTED)
        if "instagram.com/" in url:
            url = url.replace("instagram.com", "ddinstagram.com")
            url = url.replace("www.", "")
            await reply_text(message, url)
        else:
            file = await download_media(url)
            await reply_text(message, file)
            if False and file:
                temp_file = file[0]
                media_title = file[1]
                is_audio = file[2]
                if is_audio:
                    await reply_voice(message, temp_file, media_title)
                else:
                    await reply_video_new(message, temp_file)
    except Exception as e:
        await message.reply(f"[v1] Sorry, some error. {str(e)}")
        save_error(message.from_user.id, url, str(e))
    finally:
        media = media_title if file else ""
        save_stats(message.from_user.id, url, media)


async def download_media(url: str):
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
        formats = info['formats']
        filtered_formats =  list(filter(lambda x: x.get('audio_channels'), formats))

        preffered_format1080 = list(filter(lambda x: x.get('format_note') == '1080p', filtered_formats))
        preffered_format720 = list(filter(lambda x: x.get('format_note') == '720p', filtered_formats))
        preffered_format360 = list(filter(lambda x: x.get('format_note') == '360p', filtered_formats))
        
        if len(preffered_format360) > 0:
            return preffered_format360[0].get('url', 'no 360 link')
        
        if len(preffered_format720) > 0:
            return preffered_format720[0].get('url', 'no 360 link')

        #link1080 = preffered_format1080[0].get('url', 'no 720 link')
        #return link360

        #print("LINKZZZZ")

        return []
        if duration / 60 < 15:
            ydl.download([url])
        else:
            return await download_audio(url)

    return [temp_file, video_title, False]

async def download_audio(url: str):
    is_audio = True
    temp_dir = "temp"
    media_title = "untitled"
    temp_file_name = str(uuid.uuid4())
    temp_file = f"{temp_dir}/{temp_file_name}.mp3"

    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": temp_file,
        "format": "wa",
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)  # Only fetch metadata
      media_title = info.get("title", "untitled")
      filesize = info.get("filesize", 0) / 1024 / 1024  # MBytes

      if filesize <= MAX_SIZE_IN_MBYTES:
          ydl.download([url])
      else:
          raise Exception(EX_MAX_DURATION.format(MAX_SIZE_IN_MBYTES))

    return [temp_file, media_title, is_audio]

async def  get_direct_video_url(url):
  ydl = yt_dlp.YoutubeDL()
  try:
    info = ydl.extract_info(url, download=False)
    formats = copy.deepcopy(info['formats'])
    filtered_formats =  list(filter(lambda x: x.get('audio_channels'), formats))

    preffered_format1080 =  list(filter(lambda x: x.get('format_note') == '1080p', filtered_formats))
    preffered_format720 =  list(filter(lambda x: x.get('format_note') == '720p', filtered_formats))
    preffered_format360 =  list(filter(lambda x: x.get('format_note') == '360p', filtered_formats))
    #sorted_formats = sorted(filtered_formats, key=lambda fmt: fmt.get('filesize', 0) or -1, reverse=True)
    
    print("0!")

    print(f"filtered_formats - {filtered_formats.count()}" )
    print("1!")

    print(f'preffered_format360 - {preffered_format360.count()}')
    print("2!")

    print(f'preffered_format720 - {preffered_format720.count()}')
    print("3!")

    print(f'preffered_format1080 - {preffered_format1080.count()}')
    print("4!")

    # print(sorted_formats)


    link360 = preffered_format360[0].get('url', 'no 360 link')
    link720 = preffered_format720[0].get('url', 'no 720 link')
    link1080 = preffered_format1080[0].get('url', 'no 720 link')
    #linkMax = sorted_formats[0].get('url', 'no max link')


    print("LINKZZZZ")

    print(link360)
    print(link720)
    print(link1080)

    return [
            f'[360p]({link360})',
            f'[720p]({link720})',
            f'[1080p]({link1080})',
            #f'[MAX]({linkMax})', #no sound or not more than 720p
           ]
  except:
    return []