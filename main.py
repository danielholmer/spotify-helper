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
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)



@app.route('/')
def index():
    cache_path = '.cache-'.join(str(uuid.uuid4()))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path, scope='user-read-currently-playing')
    if request.args.get("code"):
        print("request.args.get('code') = True")
        session['token_info'] = auth_manager.get_access_token(request.args["code"], check_cache=False)
        #results = spotify.current_user_playing_track()
        return redirect('/')


    token_info = session.get('token_info')
    if not token_info:
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    song_info = get_song_info(spotify)



    #print("RESULTS" + results)
    #return f'<h2>Hi {spotify.me()["display_name"]}, ' \
    #       f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
    #       f'<a href="/playlists">my playlists2</a>' \
         #  f'<small>currently playing: {results} </small>'
    return render_template("index.html", song_info = song_info )

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
def get_song_info(spotify):
    song_info={}
    result = spotify.current_user_playing_track()
    print(result)
    song_info.update({"song_name": result["item"]["name"] ,
                    "artist": result["item"]["album"]["artists"][0]["name"],
                     "album": result["item"]["album"]["name"],
                     "cover_image": result["item"]["album"]["images"][0]["url"],
                     "album_type" : result["item"]["album"]["album_type"],
                     "release_date": result["item"]["album"]["release_date"]})

    #print(result["item"]["name"])
    print(result)
    return song_info
if __name__ == "__main__":
    app.run(debug=True)
