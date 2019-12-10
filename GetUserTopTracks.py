import concurrent.futures
import json
import threading
from time import sleep, time
from typing import Callable

import pandas as pd
import requests
import spotipy
import spotipy.util as util

print('check')

def get_user_token(username: str, scope: str, file: str) -> str:
    with open(file) as file:
        ID, SECRET = json.load(file).values()
        print(ID, SECRET)
    token = util.prompt_for_user_token(username,scope,
                          client_id=ID,
                          client_secret=SECRET,
                          # 注意需要在自己的web app中添加redirect url
                          redirect_uri='http://localhost/5000')
    return token

def get_user_top_tracks(user_token : str,headers)->list:
    responses = requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=medium_term&limit=100&offset=5", headers=headers)
    myjson_data = json.loads(responses.text)
    top_track_list = []
    for song in myjson_data["items"]:
        song_item = [song["name"],song["href"]]
        #song_item = {"song_name":song["name"],"href":song["href"]}
        top_track_list.append(song_item)

    return top_track_list
def write_csv(file: str, data: list):
    """
        Write csv file
        Parameter: file(string), data(dictionaries of list)
    """

    df = pd.DataFrame.from_dict(data, orient="columns")
    df.to_csv(file, index=False, encoding="utf-8")
        


if __name__ == "__main__":
    import io, sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf8")

    FILE = "user.json"
    OUTPUT_FILE = "toptracks.csv"

    token = get_user_token("virginiakm1988","user-top-read",FILE)
    headers = {"Authorization": "Bearer {}".format(token)}
    data = get_user_top_tracks(token,headers)
    write_csv(OUTPUT_FILE, data)
    #print(data)
