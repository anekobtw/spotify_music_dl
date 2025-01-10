import logging
from io import BytesIO

import aiohttp
from mutagen.id3 import APIC, ID3, TIT2, TPE1
from mutagen.mp3 import MP3
from ytmusicapi import YTMusic


def find_song(metadata: dict) -> str:
    query = f"{metadata['artist']} - {metadata['name']} {metadata['album']}"
    search_results = YTMusic().search(query, filter="songs", ignore_spelling=True)
    logging.info("Track found: %s", search_results[0]["title"])
    return "https://youtu.be/" + search_results[0]["videoId"]


async def set_track_metadata(filename: str, title: str, artist: str, thumbnail_url: str) -> None:
    audio = MP3(f"{filename}.mp3", ID3=ID3)
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as response:
            image_data = BytesIO(await response.read())
            audio.tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_data.read()))
            audio.save()
    logging.info("Metadata for track '%s' set successfully.", title)
