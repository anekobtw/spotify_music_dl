import os

from dotenv import load_dotenv

from spotify_music_dl import SpotifyDownloader

load_dotenv()
dl = SpotifyDownloader(client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"))
dl.download_track("https://open.spotify.com/track/01MWhxH5vfaCJJybmHFdcH?si=vjJ11CM3QXuy_A6b4QK4Rw")
