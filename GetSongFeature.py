import concurrent.futures
import json
from time import sleep

import pandas as pd
import requests

from GetPlaylist import get_token, print_dict, timer, use_spotipy


def read_song(id: str) -> dict:
    """
        Get song audio feature of given song
        Parameter: id(string)
        Return: dict contains information of given song
    """

    global TOKEN

    url = f"https://api.spotify.com/v1/audio-features/{id}"
    # API Limit Exceed(429 Error) Situation Handled
    response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})
    while response.status_code == 429:
        sleep(5)
        response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    content = json.loads(response.text)

    for i in ["type", "uri", "track_href", "analysis_url"]:
        del content[i]

    return content


@timer
def read_all_song(songlist: list, nameList: list) -> list:
    """ Get all of the song in numerous playlists """

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = [executor.submit(read_song, url) for url in songlist]

    songInfo = [
        content.result() for content in concurrent.futures.as_completed(results)
    ]

    return songInfo


def merge_dataframe(info: pd.DataFrame, data: list) -> pd.DataFrame:
    """ Merge two dataframe based on column 'song' """

    feature = pd.DataFrame.from_dict(data, orient="columns")

    return pd.merge(info, feature, on="id")


if __name__ == "__main__":
    import io, sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

    FILE, CSV = "user.json", "Mood.csv"
    TOKEN = get_token(FILE)
    df = pd.read_csv(CSV, engine="python")
    nameList, songList = df["song"].tolist(), df["id"].tolist()
    data = read_song("0b39vjnPaxVh6fY1Wj81MA")
    print(data)
    # data = read_all_song(songList, nameList)
    # newDf = merge_dataframe(df, data)
    # newDf.to_csv("SongInfo.csv", index=False, encoding="utf-8", mode="w", header=True)
