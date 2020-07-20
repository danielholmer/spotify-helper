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
CACHE_PATH = ".cache"

Session(app)



@app.route('/')
def index():

    #cache_path = '.cache-'.join(str(uuid.uuid4()))
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
     client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, cache_path=CACHE_PATH,
     show_dialog= True,
     scope='user-read-currently-playing user-read-private user-top-read')

    if request.args.get("code"):
        print("request.args.get('code') = True")
        session['token_info'] = auth_manager.get_access_token(request.args["code"], check_cache=False)
        #results = spotify.current_user_playing_track()
        return redirect('/')


    token_info = session.get('token_info')
    if not token_info:
        print("NOT TOKEN INFO")
        auth_url = auth_manager.get_authorize_url()
    #    auth_url = auth_url +  "show_dialog=true"
        return render_template("logon.html", auth_url = auth_url)

    spotify = spotipy.Spotify(auth=token_info['access_token'])

    try:
        song_info = get_song_info(spotify)
    except spotipy.client.SpotifyException:
        # re-authenticate when token expires
        cached_token = auth_manager.get_cached_token()
        refreshed_token = cached_token['refresh_token']
        session['token_info'] = auth_manager.refresh_access_token(refreshed_token)
        # also we need to specifically pass `auth=new_token['access_token']`
        token_info = session.get('token_info')
        spotify = spotipy.Spotify(auth=token_info['access_token'])

        song_info = get_song_info(spotify)
    display_name = get_user_info(spotify)
    if not song_info:
        return render_template("no_song.html", display_name = display_name)

    song_info = get_lyrics(song_info)




    #print("RESULTS" + results)
    #return f'<h2>Hi {spotify.me()["display_name"]}, ' \
    #       f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
    #       f'<a href="/playlists">my playlists2</a>' \
         #  f'<small>currently playing: {results} </small>'
    return render_template("index.html", song_info = song_info, display_name = display_name )

@app.route('/playlists')
def playlists():

    pass
'''
    print("playlists")

    token_info = session.get('token_info')
    if not token_info:
        return redirect('/')

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    return spotify.current_user_playlists()
'''

# https://stackoverflow.com/questions/38379507/flask-jinja2-update-div-content-without-refresh-page

@app.route('/top_songs', methods=['POST','GET'])
def top_songs():
    token_info = session.get('token_info')
    if not token_info:
        return redirect('/')

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    display_name = get_user_info(spotify)

    time_span = "short_term"
    if request.method == "POST":
        time_span = request.form['time_span']
        print(time_span)

    result = spotify.current_user_top_tracks(time_range=time_span)

    top_songs = []
    for placement, res in enumerate(result["items"],1):
        song_dict = {}
        song_dict.update({"song_name": res["name"] ,
                    "artist": res["album"]["artists"][0]["name"],
                     "placement": placement,
                     "cover_image": res["album"]["images"][2]["url"],
                     })
        top_songs.append(song_dict)
        #print(f'{placement}, {res["album"]["artists"][0]["name"]} - {res["name"]}')
        #print(res["name"])
    #print(result["items"][0]["album"]["artists"]["name"])
    print(top_songs)
    #return spotify.current_user_playlists()
    if request.method == "POST":
        return render_template("song_top_list.html", display_name=display_name, top_songs = top_songs)
    else:
        return render_template("top_songs.html", display_name=display_name, top_songs = top_songs)

@app.route("/logout/")
def logout():
    print("logout")
    session.pop('token_info', None)
    session.clear()
    #session.set_cookie("token_info", expires=0)

    #app.config['SECRET_KEY'] = os.urandom(64)
    os.remove(CACHE_PATH)
    #return redirect(url_for('index'))
    return redirect("/")

def get_user_info(spotify):

    result = spotify.current_user()
    #print(result["display_name"])
    display_name = result["display_name"]
    return display_name

def get_song_info(spotify):
    song_info={}
    result = spotify.current_user_playing_track()
    #print(result)
    if result:
        if "-" in result["item"]["name"]:
            song_name = result["item"]["name"].split("-")[0]
        else:
            song_name = result["item"]["name"]

        artist_list= []
        for artist in result["item"]["album"]["artists"]:
            print(artist["name"])
            artist_list.append(artist["name"])

        song_info.update({"song_name": song_name ,
                    "artist": artist_list,
                     "album": result["item"]["album"]["name"],
                     "cover_image": result["item"]["album"]["images"][0]["url"],
                     "album_type" : result["item"]["album"]["album_type"],
                     "release_date": result["item"]["album"]["release_date"]})

    #print(result["item"]["name"])
    #print(result)
    return song_info

def get_lyrics(song_info):
    song_lyrics=[]
    genius = lyricsgenius.Genius(GENIUS_CLIENT_ACCESS)
    try:
        #artist = genius.search_artist(song_info["artist"])
        song = genius.search_song(song_info["song_name"], song_info["artist"])
    #print(song.lyrics)
        song_lyrics = song.lyrics
        song_lyrics = song_lyrics.split('\n')
        print(song_lyrics)
    #test = ''.join('<br>' + char if char.isupper() else char.strip() for char in test).strip()
    except:
        print("error finding lyrics")
        song_lyrics.append("No lyrics found")
    #artist = genius.search_artist("Bloc Party", max_songs=3, sort="title")
    #print(artist.songs)
    song_info.update({"lyrics": song_lyrics})
    return song_info
if __name__ == "__main__":
    app.run(debug=True)