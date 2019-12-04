import json
import spotipy
import requests
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials


def get_token(file: str) -> str:
    """
        Get verified token from Spotify
        Parameter: file(json like file) contains client_id, client_secret
        Required: client_id and client_secret to access spotify API
        Return: the verified token(type: string)
    """

    with open(file) as file:
        ID, SECRET = json.load(file).values()

    url = "https://accounts.spotify.com/api/token"
    grant_type = {"grant_type": "client_credentials"}
    response = requests.post(url, data=grant_type, auth=(ID, SECRET))
    token = json.loads(response.text)["access_token"]

    return token


def use_spotipy(file: str):
    """
        Get verified access to Spotify API via using spotipy library
        Parameter: file(json like file) contains client_id, client_secret
        Required: client_id and client_secret to access spotify API
        Return: spotipy.Spotify() object
    """

    with open(file) as file:
        ID, SECRET = json.load(file).values()
    credentials = SpotifyClientCredentials(ID, SECRET)

    return spotipy.Spotify(client_credentials_manager=credentials)


def read_playlist(playlist_id: str) -> dict:
    """
        Get all tracks of given playlist
        Parameter: playlist_id(string)
        Required: playlist ID(Spotify URI)
        Return: dictionary contains information of given playlist
    """

    global TOKEN
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    return json.loads(response.text)


def read_all_playlist(playlists):
    ...


if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

    FILE = "user.json"
    TOKEN = get_token(FILE)
    playlist = read_playlist("37i9dQZF1DWWqC43bGTcPc")
    print(playlist)

