from typing import NamedTuple

# Some useful structs to store music data


class Artist(NamedTuple):
    name: str
    id: str

    def __eq__(self, other):
        return self.id == other.id


class Album(NamedTuple):
    artist_names: list[str]
    album_name: str
    album_type: str
    id: str
    cover_art: str
    url: str
    release_date: str
