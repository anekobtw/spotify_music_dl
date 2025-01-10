import asyncio
import logging
import time

import coloredlogs
import spotipy
import yt_dlp
from spotipy.oauth2 import SpotifyClientCredentials

from spotify_music_dl import helpers

coloredlogs.install(
    level="INFO",
    fmt="[%(name)s] %(message)s",
    level_styles={
        "error": {"color": "red", "bold": True},
        "info": {"color": 231, "bold": False},
    },
    field_styles={
        "name": {"color": 12, "bold": True},
    },
)


class SpotifyDownloader:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        logging.info("Spotify client initialized successfully.")

    async def get_track_metadata(self, track_url: str) -> dict:
        track = self.spotify.track(track_url)
        metadata = {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "thumbnail_url": track["album"]["images"][0]["url"],
        }
        return metadata

    async def download_track(self, track_url: str, filename: str = None) -> None:
        try:
            start = time.perf_counter()

            metadata = await self.get_track_metadata(track_url)
            if filename is None:
                filename = metadata["name"]
            if filename.endswith(".mp3"):
                filename = filename.removesuffix(".mp3")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": filename,
                "quiet": True,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            }
            url = helpers.find_song(metadata)

            logging.info("Downloading track: %s", url)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_with_yt_dlp, url, ydl_opts)

            await helpers.set_track_metadata(filename, metadata["name"], metadata["artist"], metadata["thumbnail_url"])

            end = time.perf_counter()
            logging.info("Track downloaded successfully in %d seconds", round(end - start))

        except Exception as e:
            if "403" in str(e):
                logging.error("Error 403 caught. Retrying..")
                return await self.download_track(track_url, filename)
            logging.error("Error downloading track: %s", e)
            raise

    def _download_with_yt_dlp(self, url, ydl_opts):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def download_playlist(self, playlist_url: str, directory_name: str = None) -> None:
        try:
            start = time.time()

            if directory_name is None:
                playlist = self.spotify.playlist(playlist_url)
                directory_name = playlist["name"]

            results = self.spotify.playlist_tracks(playlist_url)

            tasks = []
            for item in results["items"]:
                track_url = item["track"]["external_urls"]["spotify"]
                filename = f"{directory_name}/{item['track']['name']}"
                tasks.append(self.download_track(track_url, filename))

            logging.info("Downloading %d songs.", len(tasks))
            await asyncio.gather(*tasks)

            end = time.time()
            logging.info("Successfully downloaded playlist in %.2f seconds. ~%.2f seconds per song.", end - start, (end - start) / len(tasks))

        except Exception as e:
            logging.error("Error downloading playlist: %s", e)
            raise
