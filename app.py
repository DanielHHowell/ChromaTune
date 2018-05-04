app = dash.Dash('drug-discovery')
server = app.server

def add_markers(figure_data, plot_type = 'scatter3d' ):
    indices = []
    drug_data = figure_data[0]
    traces = []
    for point_number in indices:
        trace = dict(
            x = [ drug_data['x'][point_number] ],
            y = [ drug_data['y'][point_number] ],
            marker = dict(
                color = 'red',
                size = 16,
                opacity = 0.6,
                symbol = 'cross'
            ),
            type = plot_type
        )

        if plot_type == 'scatter3d':
            trace['z'] = [ drug_data['z'][point_number] ]

        traces.append(trace)

    return traces

BACKGROUND = 'rgb(230, 230, 230)'

COLORSCALE = [ [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"],
                [0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"] ]

def scatter_plot_3d(
        x = df['valence'],
        y = df['levels'],
        z = df['composition'],
        color = df['color'],
        xlabel = 'Valence',
        ylabel = 'Levels',
        zlabel = 'Composition',
        plot_type = 'scatter3d',
        markers = [] ):

    def axis_template_3d(title, type='linear' ):
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
            colorscale=COLORSCALE,
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
            zaxis=axis_template_3d(zlabel, 'log'),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=0.08, y=2.2, z=0.08)
            )
        )
    )

FIGURE = scatter_plot_3d()

app.layout = html.Div([
    # Row 2: Hover Panel and Graph

    html.Div([

        html.Div([

            dcc.RadioItems(
                id = 'charts_radio',
                options=[
                    dict( label='3D Scatter', value='scatter3d' ),
                    dict( label='2D Scatter', value='scatter' ),
                    dict( label='2D Histogram', value='histogram2d' ),
                ],
                labelStyle = dict(display='inline'),
                value='scatter3d'
            ),

            dcc.Graph(id='clickable-graph',
                      style=dict(width='700px'),
                      hoverData=dict( points=[dict(pointNumber=0)] ),
                      figure=FIGURE ),

        ], className='nine columns', style=dict(textAlign='center')),


    ], className='row' ),

], className='container')


if __name__ == '__main__':
    app.run_server()
