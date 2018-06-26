from flask import Flask, request, redirect, render_template, session
import spotify
import dash
import dash_core_components as dcc
import dash_html_components as html
import analysis


app = Flask(__name__)
app.secret_key = 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash')

# -------------------- DASH INITIAL LAYOUT INSTANTIATION --------------

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.7/paper/bootstrap.min.css",
                "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css",
                "https://raw.githubusercontent.com/DanielHHowell/ChromaTune/master/static/css/style.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium"]

for css in external_css:
    dash_app.css.append_css({"external_url": css})

dash_app.layout = html.Div([
                    html.Div([
                        html.Nav([
                            html.Div([

                                    #Left header
                                    html.A([
                                        html.Div([
                                            html.Img(
                                                src='https://i.imgur.com/UEH2EBT.png',
                                                style={'width':220, 'margin-top':30},
                                            ),
                                            html.Img(
                                                src='https://i.imgur.com/V5stVH0.png',
                                                style={'width':40, 'margin-top':30, 'position':'center'},
                                            ),
                                        ], className='navbar-header')
                                    ], href='http://127.0.0.1:5000'),

                                    #Right header
                                    html.Div([
                                        html.Ul([
                                            html.Li([
                                                html.Div([
                                                    html.A([

                                                        html.Div([
                                                            html.Img(src='https://i.imgur.com/pmuOmIv.png',
                                                                    style={'width':55, 'margin-top':40, 'margin-right':40, 'position':'center'})
                                                        ], className='row'),

                                                    ], href='http://127.0.0.1:5000/profile')
                                                ], className='icon-container container')
                                            ])
                                        ], className='nav navbar-nav navbar-right')
                                    ], className='navbar-collapse collapse')

                            ],className='container-fluid'),
                        ],className='navbar navbar-default'),
                    ],id='header'),

                               # Main body
                               html.Div([

                                   html.Div([
                                       html.Div([

                                           html.P(
                                               'Click back home to login and select a playlist to graph first.'),
                                       ], style={'text-align': 'center'}),

                                   ], className='jumbotron'),
                               ], className='container'),
                    ])


# ----------------------- AUTH API PROCEDURE -------------------------

@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)


@app.route("/callback/")
def callback():

    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return profile()

def valid_token(resp):
    return resp is not None and not 'error' in resp

# -------------------------- API REQUESTS ----------------------------


@app.route("/")
def index():
    return render_template('index.html')

#user-inputted axes choice
@app.route('/profile')
def profile():

    if 'auth_header' in session:
        auth_header = session['auth_header']

        profile_data = spotify.get_users_profile(auth_header)
        playlist_data = spotify.get_users_playlists(auth_header)


        if valid_token(profile_data):
            return render_template("profile.html",
                               user=profile_data,
                               playlists=playlist_data['items'])

    return render_template('profile.html')


@app.route('/playlist')
def playlist():
    if 'auth_header' in session:
        auth_header = session['auth_header']

        user_arg = request.args.get('userid')
        playlist_arg = request.args.get('id')


        results = analysis.sp.user_playlist_tracks(user_arg,
                                                    playlist_id=playlist_arg)
        playlist_tracks = results['items']
        while results['next']:
            results = analysis.sp.next(results)
            playlist_tracks.extend(results['items'])


        if valid_token(playlist_tracks):

            data = analysis.track_parse(playlist_tracks)
            df = analysis.chromatizer(data)


            # ----------------------- DASH BUILDING  -----------------------

            external_css = ["https://cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.7/paper/bootstrap.min.css",
                            "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css",
                            "https://raw.githubusercontent.com/DanielHHowell/ChromaTune/master/static/css/style.css",
                            "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                            "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                            "//fonts.googleapis.com/css?family=Dosis:Medium"]

            for css in external_css:
                dash_app.css.append_css({"external_url": css})

            BACKGROUND = 'rgb(252, 252, 252)'

            def scatter_plot_3d(
                    x=df['valence'],
                    y=df['energy'],
                    z=df['composition'],
                    color=df['color'],
                    xlabel='Valence (Hue)',
                    ylabel='Energy Level (Saturation)',
                    zlabel='Composition (Lightness)',
                    plot_type='scatter3d',
            ):

                def axis_template_3d(title, type='linear'):
                    return dict(
                        showbackground=True,
                        backgroundcolor=BACKGROUND,
                        gridcolor='rgb(225, 225, 225)',
                        title=title,
                        type=type,
                        zerolinecolor='rgb(252, 252, 252)'
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
                    showlegend=False,
                    scene=dict(
                        xaxis=axis_template_3d(xlabel),
                        yaxis=axis_template_3d(ylabel),
                        zaxis=axis_template_3d(zlabel),
                    )
                )

                return dict(data=data, layout=layout)

            FIGURE = scatter_plot_3d()

            dash_app.layout = html.Div([
                html.Div([
                    html.Nav([
                        html.Div([

                            # Left header
                            html.A([
                                html.Div([
                                    html.Img(
                                        src='https://i.imgur.com/UEH2EBT.png',
                                        style={'width': 220, 'margin-top': '12%'},
                                    ),
                                    html.Img(
                                        src='https://i.imgur.com/V5stVH0.png',
                                        style={'width': 40, 'margin-top': '12%', 'position': 'center'},
                                    ),
                                ], className='navbar-header')
                            ], href='http://127.0.0.1:5000'),

                            # Right header
                            html.Div([
                                html.Ul([
                                    html.Li([
                                        html.Div([
                                            html.A([

                                                html.Div([
                                                    html.Img(src='https://i.imgur.com/pmuOmIv.png',
                                                             style={'width': 55, 'margin-top': '30%', 'margin-right': 30,
                                                                    'position': 'center'})
                                                ], className='row'),

                                            ], href='http://127.0.0.1:5000/profile')
                                        ], className='icon-container container')
                                    ])
                                ], className='nav navbar-nav navbar-right')
                            ], className='navbar-collapse collapse')

                        ], className='container-fluid'),
                    ], className='navbar navbar-default'),
                ], id='header'),

                #Main body
                html.Div([

                    html.Div([
                        html.Div([

                                html.P(
                                    'Click and drag to rotate the graph in 3D, scroll to zoom.'),
                            ], style={'text-align':'center'}),

                    ], className='jumbotron'),
                ], className='container'),

                #Graph
                html.Div([

                    html.Div([

                        dcc.Graph(id='clickable-graph',
                                  style=dict(height='1600px', width='1750px'),
                                  hoverData=dict(points=[dict(pointNumber=0)]),
                                  figure=FIGURE),

                    ]),

                ], className='row', style={'margin-left':'15%'}),

                html.Footer([
                    html.Div([
                        html.A('by Daniel Howell',
                               href='mailto:danielhhowell@aol.com')
                    ], className='container')
                ], className='footer', style={'position':'bottom',
                                              'bottom':0, 'width':'100%',
                                              'height':60, 'line-height':60,
                                              'background-color':'#f5f5f5'})
            ])


            # ----------------------------------------------

            return render_template("playlist.html",
                               playlist=playlist_tracks)


    return render_template('playlist.html')


# ----------------------


if __name__ == "__main__":
    app.run(debug=True, threaded=True)


# ----------------------
