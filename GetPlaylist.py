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


def timer(func: Callable):
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

    nameDict = {url: name for url, name in zip(df["URL"], df["Name"])}
    return nameDict, list(nameDict.keys())


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


def read_playlist(playlist_id: str) -> list:
    """
        Get all tracks of given playlist
        Parameter: playlist_id(string)
        Required: playlist ID(Spotify URI)
        Return: list contains information of given playlist
    """

    global TOKEN
    global ALBUMDICT
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # API Limit Exceed(429 Error) Situation Handled
    response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})
    while response.status_code == 429:
        sleep(1)
        response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    content = json.loads(response.text)

    urls = list()
    for track in content["items"]:
        try:
            urls.append(
                [
                    track["track"]["name"],
                    track["track"]["id"],
                    track["track"]["album"]["artists"][0]["name"],
                    ALBUMDICT[playlist_id],
                ]
            )
        except TypeError:
            pass

    return urls


@timer
def read_all_playlist(playlists: list) -> list:
    """ Get all of the song in numerous playlists """

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = [
            executor.submit(read_playlist, collection) for collection in playlists
        ]

    collectionOfSongs = [
        {"song": song, "id": uri, "singer": singer, "album": album}
        for content in concurrent.futures.as_completed(results)
        for song, uri, singer, album in content.result()
    ]

    return collectionOfSongs


def print_dict(info: dict):
    """ print out json file pretty """
    print(json.dumps(info, indent=4))


def write_csv(file: str, data: list):
    """
        Write csv file
        Parameter: file(string), data(dictionaries of list)
    """

    df = pd.DataFrame.from_dict(data, orient="columns")
    df = df.drop_duplicates(subset="song", keep="first")
    df.to_csv(file, index=False, encoding="utf-8")


if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

    FILE, EXCEL = "user.json", "MoodPlaylist.xlsx"
    OUTPUT_FILE = "Mood.csv"
    TOKEN = get_token(FILE)
    ALBUMDICT, playlists = get_playlist_from_excel(EXCEL)
    data = read_all_playlist(playlists)
    # data = read_playlist("37i9dQZF1DX71sJP2OzuBP")
    # print(data)
    write_csv(OUTPUT_FILE, data)
