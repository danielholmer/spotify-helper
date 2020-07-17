from flask import Flask, render_template

import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
CACHE = "cache"

#SPOTIPY_CLIENT_ID = 'c6d55be5f3b848f981f5a3ed486db8d1'
#SPOTIPY_CLIENT_SECRET = 'c5f15e4f354047e2af9e2dd82e2f80b0'


app = Flask(__name__)


@app.route('/')
def main():
    test3()
    return render_template("index.html")


def test():
    scope = "user-read-currently-playing"

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, show_dialog=True, cache_path=CACHE)
    sp = spotipy.Spotify(auth_manager=auth_manager)


    #sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    #    scope=scope, show_dialog=True))
    #token = OAuth.get_access_token()
    results = sp.current_user_playing_track()
    print(results)
#    for idx, item in enumerate(results['items']):
#        track = item['track']
#        print(idx, track['artists'][0]['name'], " – ", track['name'])


def test2():


    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    user = spotify.user('masira')
    print(user)
    #if len(sys.argv) > 1:
    #    name = ' '.join(sys.argv[1:])
    #else:
    #    name = 'Radiohead'
    results =  user.current_user_playing_track()
    print(results)
    #results = spotify.search(q='artist:' + name, type='artist')
    #items = results['artists']['items']
    #if len(items) > 0:
    #    artist = items[0]
    #    print(artist['name'], artist['images'][0]['url'])


def test3():
    scope = "user-top-read"
    OAuth = SpotifyOAuth(scope=scope,
                         redirect_uri='http://localhost:8080')
    token = OAuth.get_access_token()

    # receive the following warning
    # __main__:1: DeprecationWarning: You're using 'as_dict = True'.get_access_token will return the token string directly in future
    #  versions. Please adjust your code accordingly, or use get_cached_token instead.
    # At this point, I am taken to the user authorization and grant access with the 'user-top-read' scope

    sp = spotipy.Spotify(auth_manager=OAuth)
    top_tracks = sp.current_user_top_tracks()


if __name__ == "__main__":
    app.run(debug=True)
