from dotenv.main import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

load_dotenv()

class SpotifyApi():
    def __init__(self) -> None:
        self.SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        self.SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.SPOTIFY_CLIENT_ID, client_secret=self.SPOTIFY_CLIENT_SECRET))


    def extract_meta_data(self, url: str):
        """Extracts meta data from spotify

        Returns:
            [type]: [description]
        """
        return self.sp.track(url)["name"], self.sp.track(url)["artists"]



if __name__ == '__main__':
    """This is just used for testing purposes
    """
    spotify = SpotifyApi()
    name, artists=  spotify.extract_meta_data("https://open.spotify.com/track/2fWSwWmKRuyioqIzOzuQGo?si=512d42397ec44d89")
    for artist in artists:
        print(artist["name"])


