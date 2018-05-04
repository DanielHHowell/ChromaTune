import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.tools as pt
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import flask
from flask_cors import CORS
import os
from config import *



pt.set_credentials_file(username=config().plotly_username, api_key=config().plotly_api_key)

client_id = config().spotify_client_id
client_secret = config().spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

results = sp.user_playlist_tracks(config().spotify_username,cnfig().spotify_playlist)
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
        track['composition'] = id['acousticness']*100
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
df['lightness'] = df['composition']+35
maxVal = 82
df['lightness'][df['lightness'] >= maxVal] = maxVal

# Converts the track's features to the colorsphere axes, with hue=valence, saturation=levels, and lightness=composition
df['color'] = df.apply(lambda row: 'hsl(' + str(row.valence*3.6)
                                   + ',' + str(row.levels) + '%,'
                                   + str(row.lightness) + '%)', axis=1)

app = dash.Dash('chromatune')
server = app.server

def add_markers(figure_data, plot_type = 'scatter3d' ):
    indices = []
    drug_data = figure_data[0]
    traces = []
    for point_number in indices:
        trace = dict(
            x = [drug_data['x'][point_number]],
            y = [drug_data['y'][point_number]],
            marker = dict(
                color = 'red',
                size = 16,
                opacity = 0.6,
                symbol = 'cross'
            ),
            type = plot_type
        )

        if plot_type == 'scatter3d':
            trace['z'] = [df['composition'][point_number] ]

        traces.append(trace)
    return traces

BACKGROUND = 'rgb(250, 250, 250)'

def scatter_plot_3d(
        x = df['valence'],
        y = df['levels'],
        z = df['composition'],
        color = df['color'],
        xlabel = 'Valence',
        ylabel = 'Levels',
        zlabel = 'Composition',
        plot_type = 'scatter3d',
        ):

    def axis_template_3d(title, type='linear'):
        return dict(
            showbackground = True,
            backgroundcolor = BACKGROUND,
            gridcolor = 'rgb(255, 255, 255)',
            title = title,
            type = type,
            zerolinecolor = 'rgb(255, 255, 255)'
        )


    data = [dict(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            line=dict(color='#444'),
            reversescale=True,
            sizeref=45,
            sizemode='diameter',
            opacity=0.7,
            color=color,
        ),
        text=df['name'],
        type=plot_type,
    )]

    layout = dict(
        font=dict(family='Raleway'),
        hovermode='closest',
        margin=dict(r=20, t=0, l=0, b=0),
        showlegend=False,
        scene=dict(
            xaxis=axis_template_3d(xlabel),
            yaxis=axis_template_3d(ylabel),
            zaxis=axis_template_3d(zlabel),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0.08, y=2.2, z=0.08)
            )
        )
    )

    return dict(data=data, layout=layout)

FIGURE = scatter_plot_3d()


app.layout = html.Div([

    html.Div([

        html.Div([

            dcc.Graph(id='clickable-graph',
                      style=dict(height='1000px', width='1000px'),
                      hoverData=dict( points=[dict(pointNumber=0)] ),
                      figure=FIGURE ),

        ], className='nine columns', style=dict(textAlign='center')),

    ], className='row' ),

], className='container', )


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css"]


for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server()