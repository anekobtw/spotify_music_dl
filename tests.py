import asyncio
import os

from dotenv import load_dotenv

from spotify_music_dl import SpotifyDownloader

load_dotenv()
dl = SpotifyDownloader(client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"))
asyncio.run(dl.download_track("https://open.spotify.com/track/01MWhxH5vfaCJJybmHFdcH?si=vjJ11CM3QXuy_A6b4QK4Rw", "song.mp3"))
asyncio.run(dl.download_playlist("https://open.spotify.com/playlist/6W186qF1ivh7FHLyCYAqyS?si=AKIaBh4ySo2VT-nEpLF4Dw"))
