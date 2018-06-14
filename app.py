from flask import Flask, request, redirect, render_template, session
import spotify
import dash
import dash_core_components as dcc
import dash_html_components as html
import analysis



app = Flask(__name__)
app.secret_key = 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash')

# ----------------------

dash_app.layout = html.Div([
        html.Div([

            html.H2('ChromaTune',
                    style={
                        'position': 'relative',
                        'top': '0px',
                        'left': '10px',
                        'font-family': 'Dosis',
                        'display': 'inline',
                        'font-size': '6.0rem',
                        'color': '#4D637F'
                    }),
        ], className='row twelve columns', style={'position': 'relative', 'right': '15px'})])

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


@app.route('/profile')
def profile():

    if 'auth_header' in session:
        auth_header = session['auth_header']

        profile_data = spotify.get_users_profile(auth_header)
        playlist_data = spotify.get_users_playlists(auth_header)
        recently_played = spotify.get_users_recently_played(auth_header)

        if valid_token(recently_played):
            return render_template("profile.html",
                               user=profile_data,
                               playlists=playlist_data["items"],
                               recently_played=recently_played["items"])

    return render_template('profile.html')


@app.route('/playlist')
def playlist():
    if 'auth_header' in session:
        print(session['auth_header'])
        auth_header = session['auth_header']

        user_arg = request.args.get('userid')
        playlist_arg = request.args.get('id')


        playlist_tracks = spotify.get_playlist_tracks(user_arg,
                                                      playlist_arg,
                                                      auth_header)

        if valid_token(playlist_tracks):

            data = analysis.track_parse(playlist_tracks)
            global df
            df = analysis.chromatizer(data)

            BACKGROUND = 'rgb(250, 250, 250)'

            def scatter_plot_3d(
                    x=df['valence'],
                    y=df['levels'],
                    z=df['composition'],
                    color=df['color'],
                    xlabel='Valence',
                    ylabel='Levels',
                    zlabel='Composition',
                    plot_type='scatter3d',
            ):

                def axis_template_3d(title, type='linear'):
                    return dict(
                        showbackground=True,
                        backgroundcolor=BACKGROUND,
                        gridcolor='rgb(255, 255, 255)',
                        title=title,
                        type=type,
                        zerolinecolor='rgb(255, 255, 255)'
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

            dash_app.layout = html.Div([
                html.Div([

                    html.H2('ChromaTune',
                            style={
                                'position': 'relative',
                                'top': '0px',
                                'left': '10px',
                                'font-family': 'Dosis',
                                'display': 'inline',
                                'font-size': '6.0rem',
                                'color': '#4D637F'
                            }),
                ], className='row twelve columns', style={'position': 'relative', 'right': '15px'}),

                html.Div([
                    html.Div([
                        html.Div([
                            html.P('Visualize musical qualitiies of songs in a playlist in 3 dimensions'),
                            html.P(
                                'The valence (emotional tone) of a song is represented by hue, overall energy level by saturation, and acoustic composition by lightness'),
                        ], style={'margin-left': '10px'}),
                    ], className='twelve columns')

                ], className='row'),

                html.Div([

                    html.Div([

                        dcc.Graph(id='clickable-graph',
                                  style=dict(height='1000px', width='1000px'),
                                  hoverData=dict(points=[dict(pointNumber=0)]),
                                  figure=FIGURE),

                    ], className='nine columns', style=dict(textAlign='center')),

                ], className='row'),

            ], className='container', )

            external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                            "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                            "//fonts.googleapis.com/css?family=Dosis:Medium",
                            "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css"]

            for css in external_css:
                dash_app.css.append_css({"external_url": css})

            return render_template("playlist.html",
                               playlist=playlist_tracks['items'])


    return render_template('playlist.html')


# ----------------------


if __name__ == "__main__":
    app.run(debug=True, threaded=True)


# ----------------------
