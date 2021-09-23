"""
Instructions:
TODO
Maintainer: Theodoros Giannakopoulos {tyiannak@gmail.com}
"""

# -*- coding: utf-8 -*-
import dash
from dash import dcc
from dash import dash_table
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import finnhub
import time

f = open(".finnhubkey", "r")
key = f.readline().replace("\n", "")
finnhub_client = finnhub.Client(api_key=key)
apple = finnhub_client.company_basic_financials('AAPL', 'all')
x = finnhub_client.stock_candles('AAPL', 'D',
                                 int(time.time()) - 3600 * 24 * 365 * 5,
                                 int(time.time()))


colors = {'background': '#111111', 'text': '#7FDBDD'}
fonts_histogram = dict(family="Courier New, monospace", size=12,
                      color="RebeccaPurple")

global dfs

global days_to_show
days_to_show = 30

def get_statistics(data_frames):
    stats = {}
    for name in ['c', 'h', 'l', 'o', 'v']:
        print(data_frames[name])
        stats[name] = {  'min':   float(data_frames[name].min().round(2)),
                         'mean':  float(data_frames[name].mean().round(2)),
                         'max':   float(data_frames[name].max().round(2))}
    print(stats)
    return pd.DataFrame.from_dict(stats,
                                  orient='index').reset_index().\
        to_dict('records')


def draw_data():
    # filtering:
    global days_to_show
    global dfs
    dfs = pd.DataFrame(x)
    dfs['date'] = pd.to_datetime(dfs['t'], unit='s')

    figure_1 = {'data': [go.Scatter(x=dfs.date[-days_to_show:],
                                    y=dfs.c[-days_to_show:],
                                    name="Closing",),
                         go.Scatter(x=dfs.date[-days_to_show:],
                                    y=dfs.h[-days_to_show:],
                                    name="High", ),
                         go.Scatter(x=dfs.date[-days_to_show:],
                                    y=dfs.l[-days_to_show:],
                                    name="Low", )

                         ],
                'layout': go.Layout(
                    xaxis_title="",
                    yaxis_title="Price ($)",
                    font=fonts_histogram,
                    hovermode='closest',
                    autosize=False, height=200,
                    margin={"l": 50, "r": 15, "b": 40, "t": 30, "pad": 0},
                )}

    figure_2 = {'data': [go.Scatter(x=dfs.date[-days_to_show:],
                                    y=dfs.v[-days_to_show:],
                                    name="Value",)
                         ],
                'layout': go.Layout(
                    xaxis_title="",
                    yaxis_title="Volume",
                    font=fonts_histogram,
                    hovermode='closest',
                    autosize=False, height=100,
                    margin={"l": 50, "r": 15, "b": 40, "t": 30, "pad": 0},
                )}


    table = get_statistics(dfs[-days_to_show:])

    return dcc.Graph(figure=figure_1,
                     config={'displayModeBar': False}), \
           dcc.Graph(figure=figure_2,
                     config={'displayModeBar': False}), \
           table


def get_layout():
    """
    Initialize the UI layout
    """
    cols = [{"name": "Measure", "id": "index"},
            {"name": "min", "id": "min"},
            {"name": "mean", "id": "mean"},
            {"name": "max", "id": "max"}]


    layout = dbc.Container([
        # Title
        dbc.Row(dbc.Col(html.H2("IIT Water Consumption Dash Board",
                                style={'textAlign': 'center',
                                       'color': colors['text']}))),

        # 1st Row
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure={'data': [go.Scatter(x=[1], y=[1])],},
                              config=dict(displayModeBar=False)),
                    width=12, id="hist_graph_1"),


            ]),


        # 2nd Row
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure={'data': [go.Scatter(x=[1], y=[1])], },
                              config=dict(displayModeBar=False)),
                    width=12, id="hist_graph_2"),
            ]),

        # 3rd Row
        dbc.Row(
            [
                dbc.Col(
                    dash_table.DataTable(
                        id='dataframe_output',
                        fixed_rows={'headers': True},
                        style_cell={'fontSize': 8, 'font-family': 'sans-serif',
                                    'minWidth': 10,
                                    'width': 40,
                                    'maxWidth': 95},
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        selected_columns=[],
                        selected_rows=[],
                        style_table={'height': 400},
                        virtualization=True,
                        # page_size=20,
                        columns=cols,
                        style_header={
                            'font-family': 'sans-serif',
                            'fontWeight': 'bold',
                            'font_size': '9px',
                            'color': 'white',
                            'backgroundColor': 'black'
                        },
                    ),
                    width=6
                ),
                dbc.Col(
                    html.Div([
                        dcc.Slider(id='slider_days',
                                   min=0, max=365*5, step=1, value=30),
                        html.Div(id='slider_days_container'), ]
                    ), width=2,
                ),

                dbc.Col(html.Button('Download', id='btn-download'), width=3),
            ]),

    ])

    return layout


if __name__ == '__main__':
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = get_layout()

    @app.callback(
        [dash.dependencies.Output('slider_days_container', 'children'),
         dash.dependencies.Output('hist_graph_1', 'children'),
         dash.dependencies.Output('hist_graph_2', 'children'),
         dash.dependencies.Output('dataframe_output', 'data')
         ],
        [dash.dependencies.Input('slider_days', 'value'),
         dash.dependencies.Input('btn-download', 'n_clicks')])
    def update_output(val1, val2):
        changed_id = [p['prop_id']
                      for p in dash.callback_context.triggered][0]
        if 'slider_days' in changed_id:
            global days_to_show
            days_to_show = int(val1)
        elif 'btn-download' in changed_id:
            print("TODO")
        g1, g2, tab = draw_data()
        return f'Period: {days_to_show} days', g1, g2, tab

    app.run_server(debug=True)
