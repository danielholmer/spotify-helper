"""
Written by Daniel Holmer
Based on the app.py example from the Spotipy repo: https://github.com/plamere/spotipy/blob/master/examples/app.py
Prerequisites
    pip3 install spotipy Flask Flask-Session
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // added to your [app settings](https://developer.spotify.com/dashboard/applications)
    // on Windows, use `SET` instead of `export`
Run app.py
    python3 -m flask run --port=8080
"""
import os
from flask import Flask, session, request, redirect, render_template, url_for
from flask_session import Session
import spotipy
import uuid
import lyricsgenius
from credentials import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp'
CACHE_PATH = "/tmp/.cache"

Session(app)


@app.route('/')
def index():

    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, cache_path=CACHE_PATH,
                                               show_dialog=True,
                                               scope='user-read-currently-playing user-read-private user-top-read')

    if request.args.get("code"):
        print("request.args.get('code') = True")
        session['token_info'] = auth_manager.get_access_token(
            request.args["code"], check_cache=False)

        return redirect('/')

    token_info = session.get('token_info')

    if not token_info:
        print("NOT TOKEN INFO")
        auth_url = auth_manager.get_authorize_url()

        return render_template("logon.html", auth_url=auth_url)

    spotify = spotipy.Spotify(auth=token_info['access_token'])

    try:
        song_info = get_song_info(spotify)

    except spotipy.client.SpotifyException:
        spotify = refresh_token(session, auth_manager)
        song_info = get_song_info(spotify)

    display_name = get_user_info(spotify)

    if not song_info:
        return render_template("no_song.html", display_name=display_name)

    song_info = get_lyrics(song_info)

    return render_template("index.html", song_info=song_info, display_name=display_name)


@app.route('/top_songs', methods=['POST', 'GET'])
def top_songs():

    token_info = session.get('token_info')

    if not token_info:
        return redirect('/')

    spotify = spotipy.Spotify(auth=token_info['access_token'])

    try:
        display_name = get_user_info(spotify)

    except spotipy.client.SpotifyException:
        spotify = refresh_token(session, auth_manager)
        display_name = get_user_info(spotify)

    time_span = "short_term"

    if request.method == "POST":
        time_span = request.form['time_span']
        print(time_span)

    result = spotify.current_user_top_tracks(time_range=time_span)

    top_songs = []
    for placement, res in enumerate(result["items"], 1):
        song_dict = {}
        song_dict.update({"song_name": res["name"],
                          "artist": res["album"]["artists"][0]["name"],
                          "placement": placement,
                          "cover_image": res["album"]["images"][2]["url"],
                          })
        top_songs.append(song_dict)

    if request.method == "POST":
        return render_template("song_top_list.html", display_name=display_name, top_songs=top_songs)
    else:
        return render_template("top_songs.html", display_name=display_name, top_songs=top_songs)


@app.route("/logout/")
def logout():

    session.pop('token_info', None)
    session.clear()
    os.remove(CACHE_PATH)

    return redirect("/")


def get_user_info(spotify):

    result = spotify.current_user()

    display_name = result["display_name"]
    return display_name


def get_song_info(spotify):

    song_info = {}
    result = spotify.current_user_playing_track()

    if result:
        if "-" in result["item"]["name"]:
            song_name = result["item"]["name"].split("-")[0]
        else:
            song_name = result["item"]["name"]

        artist_list = []
        for artist in result["item"]["album"]["artists"]:
            artist_list.append(artist["name"])

        song_info.update({"song_name": song_name,
                          "artist": artist_list,
                          "album": result["item"]["album"]["name"],
                          "cover_image": result["item"]["album"]["images"][0]["url"],
                          "album_type": result["item"]["album"]["album_type"],
                          "release_date": result["item"]["album"]["release_date"]})

    return song_info


def get_lyrics(song_info):
    song_lyrics = []
    genius = lyricsgenius.Genius(GENIUS_CLIENT_ACCESS)
    try:
        song = genius.search_song(song_info["song_name"], song_info["artist"])

        song_lyrics = song.lyrics
        song_lyrics = song_lyrics.split('\n')

    except:
        song_lyrics.append("No lyrics found")

    song_info.update({"lyrics": song_lyrics})
    return song_info


def refresh_token(session, auth_manager):

    cached_token = auth_manager.get_cached_token()
    refreshed_token = cached_token['refresh_token']
    session['token_info'] = auth_manager.refresh_access_token(refreshed_token)
    token_info = session.get('token_info')
    spotify = spotipy.Spotify(auth=token_info['access_token'])
    return spotify


if __name__ == "__main__":
    app.run(debug=True)
