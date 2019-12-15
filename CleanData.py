import json
import pandas as pd
import numpy as np
from numpy import mean, var, median


def clean_data(number: str) -> dict:
    tempt = {}

    loudness = data[number]["sections"]["loudness"]
    final = loudness[-5:]
    tempt["loudness_mean"] = mean(loudness)
    tempt["loudness_var"] = var(loudness)
    tempt["last_loudness_mean"] = mean(final)
    tempt["last_loudness_var"] = var(final)
    tempt["last_loudness_decrease"] = sum(
        1 if final[i] > final[i + 1] else 0 for i in range(len(final) - 1)
    )

    mode = data[number]["sections"]["mode"]
    tempt["mode_mean"] = mean(mode)
    tempt["mode_var"] = var(mode)

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

    time_signature = data[number]["sections"]["time_signature"]
    tempt["time_signature_mean"] = mean(time_signature)
    tempt["time_signature_var"] = var(time_signature)
    tempt["time_signature_has_3"] = 3 in time_signature

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

    loudness_max_time = data[number]["segments"]["loudness_max_time"]
    tempt["loudness_maxTime_min"] = min(loudness_max_time)
    tempt["loudness_maxTime_max"] = max(loudness_max_time)
    tempt["loudness_maxTime_mean"] = mean(loudness_max_time)
    tempt["loudness_maxTime_var"] = var(loudness_max_time)
    tempt["loudness_maxTime_square"] = sum((pow(i, 2) for i in loudness_max_time))

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

    # new_df.to_excel("CompleteData.xlsx", index=False, encoding="utf-8", header=True)
