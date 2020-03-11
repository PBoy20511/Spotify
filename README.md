## Music Mood Prediction

This project predict music mood by combining cognitive psychology of music and music theory.

Files to get music data:
* [GetPlaylist.py](https://github.com/yuchia0221/Spotify/blob/master/GetPlaylist.py): get songs data in Spotify playlists.
* [GetAnalysis.py](https://github.com/yuchia0221/Spotify/blob/master/GetAnalysis.py): get audio analysis data of songs.

* [GetSongFeature.py](https://github.com/yuchia0221/Spotify/blob/master/GetSongFeature.py): get music analysis data of songs.

## Requirement
To get music data, have to apply [Spotify API](https://developer.spotify.com/documentation/web-api/) and collect music data url.

* Python 3.7+
* Pandas
* Spotipy
* Requests, bs4

```bash
sudo apt-get install python3.7      # to install python
pip install pandas                  # to install pandas
```

## Execute

```bash
python [File Name]

# To execute GetPlaylist.py
python GetPlaylist.py
```
