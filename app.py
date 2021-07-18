import datetime
from flask import Flask, request, render_template
from storage_handler import StorageHandler
from spotify_api_handler import SpotifyAPIHandler

# Creating the Flask app
app = Flask(__name__)
app.jinja_env.globals.update(today=datetime.date.today)

# Initializing storage handler and loading data if available
storage_file_name = "storage.p"
storage_handler = StorageHandler(storage_file_name)
storage_handler.load()
artists = storage_handler.data

#Initialazing Spotify API Handler
spotify_handler = SpotifyAPIHandler.from_config("spotify_config.json")


#Routing
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_artist", methods=["POST"])
def add_artist():
    artists.add(spotify_handler.get_artist(request.form["query"]))
    storage_handler.save()
    return render_template("index.html", action_commited=True)


@app.route("/delete_artist", methods=["POST"])
def delete_artist():
    try:
        artists.remove(spotify_handler.get_artist(request.form["query"]))
        storage_handler.save()
        return render_template("index.html", action_commited=True)
    except:
        return render_template("index.html", action_failed=True)


@app.route("/get_albums", methods=["POST"])
def get_albums():
    starting_date = datetime.datetime(
        *list(map(int, request.form["starting_date"].split("-")))
    )
    albums = []
    include_singles = "include_singles" in request.form

    for artist in artists:
        artist_albums = spotify_handler.get_albums(
            artist.id, starting_date, include_singles
        )
        if len(artist_albums) > 0:
            albums.append([artist.name, artist_albums])
    return render_template("list_albums.html", albums=albums)


@app.route("/list_artists")
def list_artists():
    return render_template("list_artists.html", artists=artists)
