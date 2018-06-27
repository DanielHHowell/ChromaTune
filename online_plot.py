import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.tools as pt
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from config import *



pt.set_credentials_file(username=config().plotly_username, api_key=config().plotly_api_key)

client_id = config().spotify_client_id
client_secret = config().spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

results = sp.user_playlist_tracks(config().spotify_username,config().spotify_playlist)
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

uris = [i['track']['uri'] for i in tracks]
names = [i['track']['artists'][0]['name']+' - '+i['track']['name'] for i in tracks]
data = {}

def feature_collector(song):
    try:
        id = sp.audio_features(song)[0]
        track = {}
        track['levels'] = id['energy']*100
        track['valence'] = id['valence']*100
        track['composition'] = (id['acousticness']*100
        return track
    except:
        track = {}
        track['levels'] = 50
        track['valence'] = 50
        track['composition'] = 50
        return track

for i,j in enumerate(uris):
    data[j]=feature_collector(j)
    data[j]['name'] = names[i]

df = pd.DataFrame.from_dict(data, orient='index')

# Converts the track's features to the colorsphere axes, with hue=valence, saturation=levels, and lightness=composition
df['color'] = df.apply(lambda row: 'hsl(' + str(row.valence*3.6)
                                   + ',' + str(row.levels) + '%,'
                                   + str(((row.composition)/2.15)+40) + '%)', axis=1)


trace1 = go.Scatter3d(
    x=df['valence'],
    y=df['levels'],
    z=df['composition'],
    mode='markers',
    marker=dict(
        size=12,
        color=df['color'],                # set color to an array/list of desired values
        colorscale='Viridis',   # choose a colorscale
        opacity=0.78
    ),
    text = df['name']

)

data = [trace1]
layout = go.Layout(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    ),
    title= 'Colorsphere of Musical Qualities',
        hovermode= 'closest',
        xaxis= dict(
            title= 'Valence',
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= 'Level',
            ticklen= 5,
            gridwidth= 2,
        ),
        zaxis=dict(
            title= 'Composition',
            ticklen= 5,
            gridwidth= 2,
        ),

        showlegend= True
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='3d-scatter-colorscale')