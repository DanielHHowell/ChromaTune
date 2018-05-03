import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.tools as pt
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import pandas as pd



pt.set_credentials_file(username='danielhhowell', api_key='JS9gAxQhNlsv2kih2OKW')

client_id = 'eba63584a115452f902d42dee57a5e48'
client_secret = '88652f89c3b94d4abf858779a9807ee3'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

results = sp.user_playlist_tracks('tyrosanity','3Q8DsraSJ9JIfiIr4wtyuv')
tracks = results['items']
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

uris = [i['track']['uri'] for i in tracks]
names = [i['track']['name'] for i in tracks]
data = {}

def feature_collector(song):
    try:
        id = sp.audio_features(song)[0]
        track = {}
        track['levels'] = id['energy']
        track['valence'] = id['valence']
        track['composition'] = id['acousticness']
        return track
    except:
        track = {}
        track['levels'] = 0.5
        track['valence'] = 0.5
        track['composition'] = 0.5
        return track

for i,j in enumerate(uris):
    data[j]=feature_collector(j)
    data[j]['name'] = names[i]

df = pd.DataFrame.from_dict(data, orient='index')
df['color'] =


# x = [data[i]['levels'] for i in data]
# y = [data[i]['valence'] for i in data]
# z = [data[i]['composition'] for i in data]

# c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(z))]

trace1 = go.Scatter3d(
    x=df['levels'],
    y=df['valence'],
    z=df['composition'],
    mode='markers',
    marker=dict(
        size=12,
        color=df['valence'],                # set color to an array/list of desired values
        colorscale='Viridis',   # choose a colorscale
        opacity=0.8
    ),
    text = names

)

data = [trace1]
layout = go.Layout(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    )
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='3d-scatter-colorscale')



