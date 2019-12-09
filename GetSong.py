import concurrent.futures
import json
from time import sleep

import pandas as pd
import requests

from GetPlaylist import get_token, print_dict, timer, use_spotipy


def read_song(url: str) -> list:
    """
        Get song audio feature of given song
        Parameter: url(string)
        Required: track URL(Spotify Track URI)
        Return: list contains information of given song
    """

    global TOKEN

    # API Limit Exceed(429 Error) Situation Handled
    response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})
    while response.status_code == 429:
        sleep(5)
        response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    content = json.loads(response.text)
    for i in ["type", "id", "uri", "track_href", "analysis_url"]:
        del content[i]

    return content.items()


@timer
def read_all_song(songlist: list, nameList: list) -> list:
    """ Get all of the song in numerous playlists """

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = [executor.submit(read_song, url) for url in songlist]

    songInfo = [
        dict(**{"song": name}, **{k: v for k, v in content.result()})
        for name, content in zip(nameList, concurrent.futures.as_completed(results))
    ]

    return songInfo


def merge_dataframe(info: pd.DataFrame, data: list) -> pd.DataFrame:
    """ Merge two dataframe based on column 'song' """

    feature = pd.DataFrame.from_dict(data, orient="columns")
    newDf = pd.merge(info, feature, on="song")
    newDf = newDf.drop_duplicates(subset=["song"], keep="first")
    return newDf


if __name__ == "__main__":
    import io, sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

    FILE, CSV = "user.json", "情調.csv"
    TOKEN = get_token(FILE)
    df = pd.read_csv(CSV)
    nameList = df["song"].tolist()
    songList = df["url"].apply(lambda x: x.replace("tracks", "audio-features")).tolist()
    data = read_all_song(songList, nameList)
    # print(read_song("https://api.spotify.com/v1/audio-features/4TBBPZks71c60whhq0PgdP"))
    # print(data)
    newDf = merge_dataframe(df, data)
    newDf.to_csv("TEST.csv", index=False, encoding="utf-8")
