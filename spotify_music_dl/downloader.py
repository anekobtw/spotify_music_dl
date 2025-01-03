import logging
import time
from io import BytesIO
from re import search

import coloredlogs
import requests
import spotipy
import yt_dlp
from mutagen.id3 import APIC, ID3, TIT2, TPE1
from mutagen.mp3 import MP3
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic

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
        self.ytmusic = YTMusic()
        self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        logging.info("Spotify and YTMusic clients initialized successfully.")

    def get_track_metadata(self, track_url: str) -> dict[str, str]:
        logging.info(f"Fetching metadata for track: {track_url}")
        track = self.spotify.track(track_url)
        metadata = {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "thumbnail_url": track["album"]["images"][0]["url"],
        }
        logging.info(f"Metadata fetched successfully: {metadata}")
        return metadata

    def find_song(self, track_url: str) -> str:
        metadata = self.get_track_metadata(track_url)
        query = f"{metadata['artist']} - {metadata['name']} {metadata['album']}"
        search_results = self.ytmusic.search(query, filter="songs", ignore_spelling=True)
        logging.info(f"Track found: {search_results[0]["title"]}")
        return "https://youtu.be/" + search_results[0]["videoId"]

    def set_track_metadata(self, filename: str, title: str, artist: str, thumbnail_url: str) -> None:
        audio = MP3(f"{filename}.mp3", ID3=ID3)
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))

        response = requests.get(thumbnail_url)
        image_data = BytesIO(response.content)
        audio.tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_data.read()))

        audio.save()

    def download_track(self, track_url: str, filename: str = None) -> None:
        try:
            start = time.perf_counter()

            metadata = self.get_track_metadata(track_url)
            if filename == None:
                filename = metadata["name"]
            if filename.endswith(".mp3"):
                filename.removesuffix(".mp3")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": filename,
                "quiet": True,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                url = self.find_song(track_url)
                logging.info(f"Downloading track: {url}")
                ydl.download(url)

            self.set_track_metadata(filename, metadata["name"], metadata["artist"], metadata["thumbnail_url"])

            end = time.perf_counter()
            logging.info(f"Track downloaded successfully in {round(end-start)} seconds")

        except Exception as e:
            logging.error(f"Error downloading track: {e}")
            raise

    def download_playlist(self, playlist_url: str, directory_name: str = None) -> None:
        try:
            if directory_name == None:
                playlist = self.spotify.playlist(playlist_url)
                directory_name = playlist["name"]

            results = self.spotify.playlist_tracks(playlist_url)
            for item in results["items"]:
                metadata = self.get_track_metadata(item["track"]["external_urls"]["spotify"])
                self.download_track(item["track"]["external_urls"]["spotify"], filename=f"{directory_name}/{metadata['name']}.%(ext)s")
        except Exception as e:
            logging.error(f"Error downloading track: {e}")
            raise
