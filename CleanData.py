import json
import pandas as pd
import numpy as np
from numpy import mean, var, median


def clean_data(number: str) -> dict:
    """ Create Features based on Spotify analysis data and will be stored in dictionary """

    tempt = {}

    """
    Loudness values are useful for comparing relative loudness of sections within tracks
        - Get whole sections and last five sections loudness for mean and variance value, respectively
        - Furthermore, find out does the loudness decrease (ai > ai+1) in last five sections
    """
    loudness = data[number]["sections"]["loudness"]
    final = loudness[-5:]
    tempt["loudness_mean"] = mean(loudness)
    tempt["loudness_var"] = var(loudness)
    tempt["last_loudness_mean"] = mean(final)
    tempt["last_loudness_var"] = var(final)
    tempt["last_loudness_decrease"] = sum(
        1 if final[i] > final[i + 1] else 0 for i in range(len(final) - 1)
    )

    """
    Indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. 
    This field will contain a 0 for “minor”, a 1 for “major”, or a -1 for no result
        - Get whole sections mode mean and variance value
    """
    mode = data[number]["sections"]["mode"]
    tempt["mode_mean"] = mean(mode)
    tempt["mode_var"] = var(mode)

    """
    The values of key ranging from 0 to 11 mapping to pitches using standard Pitch Class notation
        - Get whole sections key for min, max, and median value
        - Furthermore, find out does the key decrease (ai > ai+1) in last five sections and whole sections
        - url: https://en.wikipedia.org/wiki/Pitch_class
    """
    key = data[number]["sections"]["key"]
    final = key[-5:]
    tempt["key_min"] = min(key)
    tempt["key_max"] = max(key)
    tempt["key_median"] = median(key)
    tempt["key_decrease"] = sum(
        1 if key[i] > key[i + 1] else 0 for i in range(len(key) - 1)
    )
    tempt["last_key_decrease"] = sum(
        1 if final[i] > final[i + 1] else 0 for i in range(len(final) - 1)
    )

    """
    The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure)
    The time signature ranges from 3 to 7 indicating time signatures of “3/4”, to “7/4”
        - Get whole sections time_signature mean and variance value and finding is mode=3 in this song
    """
    time_signature = data[number]["sections"]["time_signature"]
    tempt["time_signature_mean"] = mean(time_signature)
    tempt["time_signature_var"] = var(time_signature)
    tempt["time_signature_has_3"] = 3 in time_signature

    """
    In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
        - Get whole sections and last five sections tempo for mean and variance value, respectively
        - Furthermore, find out does the tempo decrease (ai > ai+1) in last five sections and whole sections
    """
    tempo = data[number]["sections"]["tempo"]
    final = tempo[-5:]
    tempt["tempo_mean"] = mean(tempo)
    tempt["tempo_var"] = var(tempo)
    tempt["last_tempo_mean"] = mean(final)
    tempt["last_tempo_var"] = var(final)
    tempt["tempo_decrease"] = sum(
        1 if tempo[i] > tempo[i + 1] else 0 for i in range(len(tempo) - 1)
    )
    tempt["last_tempo_decrease"] = sum(
        1 if final[i] > final[i + 1] else 0 for i in range(len(final) - 1)
    )

    """
    The segment-relative offset of the segment peak loudness in seconds
    Can be used to describe the “attack” of the segment
        - Get whole sections loudness_max_time min, max, mean, and variance value
        - Furthermore, calculate the squared sum of loudness_max_time
    """
    loudness_max_time = data[number]["segments"]["loudness_max_time"]
    tempt["loudness_maxTime_min"] = min(loudness_max_time)
    tempt["loudness_maxTime_max"] = max(loudness_max_time)
    tempt["loudness_maxTime_mean"] = mean(loudness_max_time)
    tempt["loudness_maxTime_var"] = var(loudness_max_time)
    tempt["loudness_maxTime_square"] = sum((pow(i, 2) for i in loudness_max_time))

    """
    For completeness however, the first dimension represents the average loudness of the segment; 
    second emphasizes brightness; third is more closely correlated to the flatness of a sound; 
    fourth to sounds with a stronger attack; etc. See an image below representing the 12 basis functions.
    The actual timbre of the segment is best described as a "linear combination" of these 12 basis functions 
    weighted by the coefficient values: timbre = c1 x b1 + c2 x b2 + … + c12 x b12, where c1 to c12 
    represent the 12 coefficients and b1 to b12 the 12 basis functions as displayed below. 
    Timbre vectors are best used in comparison with each other.
        - Compute every basis mean, variance, median, min, and max value
    """
    timbre = [i for i in zip(*data[number]["segments"]["timbre"])]
    for i in range(len(timbre)):
        tempt[f"Basis{i + 1}_mean"] = mean(timbre[i])
        tempt[f"Basis{i + 1}_var"] = var(timbre[i])
        tempt[f"Basis{i + 1}_median"] = median(timbre[i])
        tempt[f"Basis{i + 1}_min"] = min(timbre[i])
        tempt[f"Basis{i + 1}_max"] = max(timbre[i])

    return tempt


if __name__ == "__main__":
    with open("data/first_clean.json", "r") as file:
        data = json.load(file)

    for i in data.keys():
        data[i] = clean_data(i)

    data = [{"id": i, **data[i]} for i in data]
    feature = pd.DataFrame.from_dict(data, orient="columns")

    df = pd.read_csv("SongInfo.csv")
    df = df.drop_duplicates(subset="id")
    df = df.drop("key", axis=1)

    new_df = pd.merge(df, feature, on="id")

    # new_df.to_excel("FILENAME.xlsx", index=False, encoding="utf-8", header=True)
