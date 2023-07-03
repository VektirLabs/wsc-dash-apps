import dash
import time
from dash import html, dcc
import dash_bootstrap_components as dbc
from utils import con_corva as cc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from dash import exceptions as e
from comp.offcanvas import templater_sidebar #sidebar

# --- Register pages ------------------------------------------------
dash.register_page(
    __name__,
    path='/tallyblaster_app',
    title='WSC - Tally Blaster App',
    name='WSC - Tally Blaster App'
)
layout = html.Div(children=[
     html.H3(
            children=[
                html.Img(src='https://img.icons8.com/external-chloe-kerismaker/64/external-Cannon-carnival-chloe-kerismaker.png', 
                            style={'height':'40px', 'margin-right':'10px'}),
                'Tally Blaster App',
            ],
        style={'margin-top': '-35px'}
        ), 
        html.Hr(),

    html.Div(children='''
        This is our Tally Blaster App page content. Clearly a  work in progress...
    '''),
])