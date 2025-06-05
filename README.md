# Coding Projects

## Spotify Playlist Creator

This repository contains a simple Python script that can read a JSON file with track information and automatically create a playlist in your Spotify account.

### Prerequisites

- Python 3
- [Spotipy](https://spotipy.readthedocs.io/) (installed automatically if you run `pip install -r requirements.txt`)
- Spotify developer credentials set in the environment variables `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI`.

### Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Prepare a JSON file, e.g. `tracks.json`:

```json
{
  "playlist_name": "My Imported Playlist",
  "tracks": [
    {"artist": "Radiohead", "title": "Paranoid Android"},
    {"artist": "Daft Punk", "title": "Harder Better Faster Stronger"}
  ]
}
```

3. Run the script:

```bash
python create_playlist_from_json.py tracks.json
```

The script will search Spotify for each track and add the results to a private playlist in your account. When the input is grouped by artist and album, a separate playlist will be created for each album.

Alternatively, you can supply a nested JSON structure containing file names. The
script will parse strings of the form `Artist - Title.ext` and search Spotify for
those tracks:

```json
{
  "playlist_name": "GI-DLE Favorites",
  "(G)I-DLE": {
    "2": [
      "(G)I-DLE - 7Days.flac",
      "(G)I-DLE - Doll.flac"
    ]
  }
}
```

When the JSON file is organized by artist and album, a separate playlist will be
created for each album. For example:

```json
{
  "(G)I-DLE": {
    "2": [
      "(G)I-DLE - 7Days.flac",
      "(G)I-DLE - Doll.flac"
    ],
    "I Feel": [
      "(G)I-DLE - Allergy.flac",
      "(G)I-DLE - Queencard.flac"
    ]
  },
  "Metallica": {
    "Ride the Lightning": [
      "Metallica - Fade to Black.flac"
    ]
  }
}
```

Running the script on such a file will create playlists named `(G)I-DLE - 2`, `(G)I-DLE - I Feel`, and `Metallica - Ride the Lightning`.
