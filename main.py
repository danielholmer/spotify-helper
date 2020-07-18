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

GENIUS_CLIENT_ACCESS = "gwPJBes0Ai9I7S6_3MWXhfV09Bba30t_TpYmGoPi79GlFhHZ_W7HGogczi6WLO0F"
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
CACHE_PATH = ".cache"

Session(app)



@app.route('/')
def index():

    #cache_path = '.cache-'.join(str(uuid.uuid4()))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=CACHE_PATH, scope='user-read-currently-playing user-read-private user-top-read')

    if request.args.get("code"):
        print("request.args.get('code') = True")
        session['token_info'] = auth_manager.get_access_token(request.args["code"], check_cache=False)
        #results = spotify.current_user_playing_track()
        return redirect('/')


    token_info = session.get('token_info')
    if not token_info:
        print("NOT TOKEN INFO")
        auth_url = auth_manager.get_authorize_url()
        return render_template("logon.html", auth_url = auth_url)

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    song_info = get_song_info(spotify)

    if not song_info:
        return render_template("no_song.html")

    song_info = get_lyrics(song_info)
    display_name = get_user_info(spotify)



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

@app.route('/top_songs')
def top_songs():
    token_info = session.get('token_info')
    if not token_info:
        return redirect('/')

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    display_name = get_user_info(spotify)

    result = spotify.current_user_top_tracks(time_range='short_term')

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
    return render_template("top_songs.html", display_name=display_name, top_songs = top_songs)

@app.route("/logout/")
def logout():
    session.pop('token_info', None)

    #app.config['SECRET_KEY'] = os.urandom(64)
    os.remove(CACHE_PATH)
    return redirect(url_for('index'))

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
        artist_list= []
        for artist in result["item"]["album"]["artists"]:
            print(artist["name"])
            artist_list.append(artist["name"])
        song_info.update({"song_name": result["item"]["name"] ,
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
