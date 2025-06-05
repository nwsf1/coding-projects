import json
import os
import sys
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


def _parse_track_string(track_str):
    """Return a dict with artist and title parsed from a filename."""
    base = os.path.basename(track_str)
    base = os.path.splitext(base)[0]
    if " - " in base:
        artist, title = base.split(" - ", 1)
    else:
        artist, title = None, base
    return {"artist": artist, "title": title}


def _gather_tracks(obj, tracks, artist=None, album=None):
    """Recursively collect tracks from arbitrary JSON structures."""
    if isinstance(obj, dict):
        if "tracks" in obj and isinstance(obj["tracks"], list):
            for t in obj["tracks"]:
                if isinstance(t, str):
                    track = _parse_track_string(t)
                else:
                    track = dict(t)
                if artist and not track.get("artist"):
                    track["artist"] = artist
                if album:
                    track["album"] = album
                tracks.append(track)
        else:
            for key, val in obj.items():
                _gather_tracks(val, tracks, artist=artist or key, album=album)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _gather_tracks(item, tracks, artist=artist, album=album)
            elif isinstance(item, str):
                track = _parse_track_string(item)
                if artist and not track.get("artist"):
                    track["artist"] = artist
                if album:
                    track["album"] = album
                tracks.append(track)


def _load_playlists(json_path):
    """Return a mapping of playlist name to tracks."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Explicit playlist with optional nested track list
    if isinstance(data, dict) and (
        "tracks" in data or "playlist_name" in data
    ):
        playlist_name = data.get("playlist_name", "Imported Playlist")
        payload = data.get("tracks", data)
        tracks = []
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, str):
                    tracks.append(_parse_track_string(item))
                else:
                    tracks.append(item)
        else:
            _gather_tracks(payload, tracks)
        return {playlist_name: tracks}

    # Otherwise treat as artist -> album mapping
    playlists = {}
    for artist, albums in data.items():
        if not isinstance(albums, dict):
            continue
        for album, payload in albums.items():
            tracks = []
            _gather_tracks(payload, tracks, artist=artist, album=album)
            playlists[f"{artist} - {album}"] = tracks

    return playlists


def create_playlists(json_path):
    playlists = _load_playlists(json_path)
    if not playlists:
        print("No tracks found in JSON", file=sys.stderr)
        return

    sp = Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private"))
    user_id = sp.me()["id"]

    for playlist_name, tracks in playlists.items():
        if not tracks:
            continue
        playlist = sp.user_playlist_create(
            user=user_id, name=playlist_name, public=False
        )
        playlist_id = playlist["id"]

        track_uris = []
        for track in tracks:
            if "uri" in track:
                track_uris.append(track["uri"])
                continue
            artist = track.get("artist")
            title = track.get("title") or track.get("name")
            album = track.get("album")
            if not title:
                continue
            query = f"{title}"
            if artist:
                query += f" artist:{artist}"
            if album:
                query += f" album:{album}"
            result = sp.search(q=query, type="track", limit=1)
            items = result.get("tracks", {}).get("items")
            if items:
                track_uris.append(items[0]["uri"])
            else:
                print(
                    f"Track not found: {title} - {artist} ({album})",
                    file=sys.stderr,
                )

        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(playlist_id, track_uris[i : i + 100])

        print(f"Created playlist '{playlist_name}' with {len(track_uris)} tracks")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <tracks.json>")
        sys.exit(1)
    create_playlists(sys.argv[1])
