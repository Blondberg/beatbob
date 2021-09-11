from dotenv.main import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os


class SpotifyApi():
    def __init__(self) -> None:
        self.SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        self.SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.SPOTIFY_CLIENT_ID, client_secret=self.SPOTIFY_CLIENT_SECRET))

    def extract_meta_data(link: str):
        """Extracts meta data from spotify

        Returns:
            [type]: [description]
        """
        return link


# results = sp.search(q='e7c2dbfabc554a7f', limit=20)
# results = sp.artist("")
# for idx, track in enumerate(results['tracks']['items']):
#     print(idx, track['name'])



