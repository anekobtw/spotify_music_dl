from spotify_music_dl import SpotifyDownloader
from dotenv import load_dotenv
import os

load_dotenv()
dl = SpotifyDownloader(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
)
dl.download_playlist("https://open.spotify.com/playlist/5AHH67GYsljwoB1q6UGvWg?si=LLFyrho2SwaMehMWj2Iylw&pi=e-OU8F2q3wSb23")
