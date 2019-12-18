import json
from time import sleep

import numpy as np
import pandas as pd
import requests

from GetPlaylist import get_token, print_dict, timer, use_spotipy


def get_track_analysis(id: str) -> dict:
    """ 
        Get track audio-analysis from Spotify API
        Parameter: id(track id)
        Return: Spotify response data
    """

    global TOKEN

    url = f"https://api.spotify.com/v1/audio-analysis/{id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    # Handle errors may occur
    while response.status_code == 429 or response.status_code == 504:
        response = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})

    return json.loads(response.text)


def get_all_data(id_list: list) -> dict:
    """ 
        Get all tracks audio-analysis from Spotify API
        Parameter: id_list(track ids stored in a list)
        Return: A dictionary {"id": Spotify response data}
    """

    data = {}
    counter = len(id_list)
    for i in id_list:
        data[i] = get_track_analysis(i)
        counter -= 1
        if counter % 100 == 0:
            print(f"{counter} song(s) remaining")
        else:
            print("Done", end="\t")

    print("Finished !!!!")

    return data


def combine_data(data: dict) -> dict:
    """ Clean all data """

    keys = data.keys()

    for number in keys:
        tempt = {}
        loudness, tempo, mode, time_signature, key = [], [], [], [], []
        for i in data[number]["sections"]:
            loudness.append(i["loudness"])
            tempo.append(i["tempo"])
            mode.append(i["mode"])
            time_signature.append(i["time_signature"])
            key.append(i["key"])

        tempt["sections"] = {
            "loudness": loudness,
            "tempo": tempo,
            "mode": mode,
            "time_signature": time_signature,
            "key": key,
        }

        loudness_max_time, timbre = [], []
        for i in data[number]["segments"]:
            loudness_max_time.append(i["loudness_max_time"])
            timbre.append(i["timbre"])

        tempt["segments"] = {"loudness_max_time": loudness_max_time, "timbre": timbre}
        data[number] = tempt

    return data


if __name__ == "__main__":
    TOKEN = get_token("user.json")
    df = pd.read_csv("SongInfo.csv")

    # Capture 500 songs of audio-analysis should take a while
    id_list = df["id"].tolist()[0:500]
    data = get_all_data(id_list)

    # Write into a json file(size: around 1.5GB for 500 songs)
    with open("analysis.json", "w+", encoding="utf-8") as file:
        json.dump(data, file)

    # lists of json file you like to merge
    jsonList = ["analysis.json"]
    data = {}
    for file in jsonList:
        with open(file, "r") as f:
            data = {**data, **json.load(f)}

    # Clean data and
    clean_data = combine_data(data)
    with open("data/clean.json", "w+", encoding="utf-8") as file:
        json.dump(clean_data, file)
