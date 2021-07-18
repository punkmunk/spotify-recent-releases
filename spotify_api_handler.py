import datetime
import requests
import base64
from urllib.parse import urlencode
import json

from music_structs import Album, Artist


class SpotifyAPIHandler:
    # A somewhat simple wrapper for Spotify Web API

    token = None

    def __init__(self, client_id: str, client_secret: str):
        self.credentials = f"{client_id}:{client_secret}"
        self.credentials = base64.b64encode(self.credentials.encode())
        self.credentials = self.credentials.decode()

    @staticmethod
    def from_config(config_path: str):
        with open(config_path, "r") as f:
            spotify_keys = json.load(f)
        return SpotifyAPIHandler(
            spotify_keys["client_id"], spotify_keys["client_secret"]
        )

    def get_token(self):
        auth_url = "https://accounts.spotify.com/api/token"
        headers = {"Authorization": f"Basic {self.credentials}"}

        data = {"grant_type": "client_credentials"}

        response = requests.post(auth_url, headers=headers, data=data)
        response_data = response.json()
        self.token = response_data["access_token"]
        self.expires = datetime.datetime.now() + datetime.timedelta(
            seconds=response_data["expires_in"]
        )

    def token_expired(self) -> bool:
        return not self.token or self.expires <= datetime.datetime.now()

    def refresh_token(self):
        if self.token_expired():
            self.get_token()

    def get_artist(self, query: str) -> str:
        self.refresh_token()
        search_url = "https://api.spotify.com/v1/search"

        headers = {"Authorization": f"Bearer {self.token}"}

        params = {"q": query, "type": "artist"}

        response = requests.get(f"{search_url}?{urlencode(params)}", headers=headers)
        artist_name = response.json()["artists"]["items"][0]["name"]
        artist_id = response.json()["artists"]["items"][0]["id"]
        return Artist(artist_name, artist_id)

    def get_albums(
        self, artist_id: str, starting_date: datetime.datetime, include_singles: bool
    ) -> list[Album]:
        self.refresh_token()
        albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        limit = 50

        headers = {"Authorization": f"Bearer {self.token}"}

        params = {
            "type": "artist",
            "market": "RU",
            "limit": limit,
            "include_groups": "album",
        }

        if include_singles:
            params["include_groups"] += ",single"

        albums = []
        albums_left = True
        album_names = set()
        while albums_left:
            response = requests.get(
                f"{albums_url}?{urlencode(params)}", headers=headers
            )
            response_items = response.json()["items"]
            if len(response_items) == 0:
                albums_left = False
            else:
                for album in response_items:
                    if album["name"] in album_names:
                        continue
                    else:
                        album_names.add(album["name"])
                    release_date = album["release_date"]
                    release_date = list(map(int, release_date.split("-")))
                    release_date = release_date + [1] * (3 - len(release_date))
                    release_date = datetime.datetime(*release_date)
                    if starting_date > release_date:
                        albums_left = False
                    else:
                        albums.append(
                            Album(
                                artist_names=[
                                    album["artists"][i]["name"]
                                    for i in range(len(album["artists"]))
                                ],
                                album_name=album["name"],
                                album_type=album["album_type"].capitalize(),
                                id=album["id"],
                                cover_art=album["images"][0]["url"],
                                url=album["external_urls"]["spotify"],
                                release_date=album["release_date"],
                            )
                        )

                params["offset"] = params.get("offset", 0) + limit
        return albums
