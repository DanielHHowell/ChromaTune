import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from config import *

client_id = config().spotify_client_id
client_secret = config().spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Gathering URIs when run as standalone
# ----------------

# results = sp.user_playlist_tracks(config().spotify_username,config().spotify_playlist)
# tracks = results['items']
# while results['next']:
#     results = sp.next(results)
#     tracks.extend(results['items'])


def feature_collector(song):

    track = {}
    try:
        id = sp.audio_features(song)[0]
        track['levels'] = id['energy']*100
        track['valence'] = id['valence']*100
        track['composition'] = id['acousticness']*100
        return track
    except:
        track['levels'] = 50
        track['valence'] = 50
        track['composition'] = 50
        return track

def track_parse(playlistdata):

    uris = [i['track']['uri'] for i in playlistdata['items']]
    names = [i['track']['artists'][0]['name'] + ' - ' + i['track']['name'] for i in playlistdata['items']]
    data = {}
    for i, j in enumerate(uris):
        data[j] = feature_collector(j)
        data[j]['name'] = names[i]
    return data


def chromatizer(playlistdict):
    df = pd.DataFrame.from_dict(playlistdict, orient='index')
    df['lightness'] = df['composition'] + 35
    maxVal = 82
    df['lightness'][df['lightness'] >= maxVal] = maxVal

    # Converts the track's features to the colorsphere axes, with hue=valence, saturation=levels, and lightness=composition
    df['color'] = df.apply(lambda row: 'hsl(' + str(row.valence * 3.6)
                                       + ',' + str(row.levels) + '%,'
                                       + str(row.lightness) + '%)', axis=1)

    return df
