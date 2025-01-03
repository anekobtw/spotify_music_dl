import logging
import time
from re import search

import coloredlogs
import spotipy
import yt_dlp
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
        }
        logging.info(f"Metadata fetched successfully: {metadata}")
        return metadata

    def download_track(self, track_url: str, filename: str = None) -> None:
        try:
            start = time.perf_counter()

            # Search
            metadata = self.get_track_metadata(track_url)
            query = f"{metadata['artist']} - {metadata['name']} {metadata['album']}"
            search_results = self.ytmusic.search(query, filter="songs", ignore_spelling=True)
            url = "https://youtu.be/" + search_results[0]["videoId"]
            logging.info(f"Track found: {search_results[0]["title"]}")

            # Download
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": filename if filename is not None else f"{metadata['name']}.%(ext)s",
                "quiet": True,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logging.info(f"Downloading track: {url}")
                ydl.download(url)
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
            for item in results['items']:
                metadata = self.get_track_metadata(item['track']['external_urls']['spotify'])
                self.download_track(item['track']['external_urls']['spotify'], filename=f"{directory_name}/{metadata['name']}.%(ext)s")
        except Exception as e:
            logging.error(f"Error downloading track: {e}")
            raise
