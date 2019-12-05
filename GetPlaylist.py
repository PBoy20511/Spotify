import concurrent.futures
import json
import threading
from time import sleep, time
from typing import Callable

import pandas as pd
import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials


def timer(func):
    """ Count how many time this function run """

    def inner(*args, **kwargs):
        before = time()
        f = func(*args, *kwargs)
        print(f"Duration: {time() - before:.1f}s")
        return f

    return inner


def get_playlist_from_excel(file: str) -> tuple:
    """
        Get the urls from given excel file
        Parameter: excel file name
        Required: excel file at least contains a column called "URL" 
        Return: a list of urls and playlist name
    """

    df = pd.read_excel(file)
    df["URL"] = df["URL"].apply(lambda x: x[17:])
    return df["Name"].tolist(), df["URL"].tolist()


def get_token(file: str) -> str:
    """
        Get verified token from Spotify
        Parameter: file name (json like file)
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


def use_spotipy(file: str) -> Callable:
    """
        Get verified access to Spotify API via using spotipy library
        Parameter: file name(json like file)
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

    # API Limit Exceed(429 Error) Situation Handled
    response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})
    while response.status_code == 429:
        sleep(1)
        response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    content = json.loads(response.text)

    urls = dict()
    for track in content["items"]:
        try:
            urls[track["track"]["name"]] = track["track"]["href"]
        except TypeError:
            pass
    
    return urls


@timer
def read_all_playlist(playlists: list) -> dict:
    """ Get all of the song in numerous playlists """

    global name
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = [
            executor.submit(read_playlist, collection) for collection in playlists
        ]

    collectionOfSongs = {
        album: content.result()
        for album, content in zip(name, concurrent.futures.as_completed(results))
    }

    return collectionOfSongs


def print_dict(info: dict):
    """ print out json file pretty """
    print(json.dumps(info, indent=4))


if __name__ == "__main__":
    import io, sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

    FILE, EXCEL = "user.json", "MoodPlaylist.xlsx"
    TOKEN = get_token(FILE)
    name, playlists = get_playlist_from_excel(EXCEL)
    a = read_all_playlist(playlists)
    # print(a)
