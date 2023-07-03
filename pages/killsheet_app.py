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
    path='/killsheet_app',
    title='WSC - Kill Sheet App',
    name='WSC - Kill Sheet App'
)
layout = html.Div(children=[
     html.H3(
            children=[
                html.Img(src='https://img.icons8.com/officel/100/pressure.png', 
                            style={'height':'40px', 'margin-right':'10px'}),
                'Kill Sheet App',
            ],
        style={'margin-top': '-35px'}
        ), 
        html.Hr(),

    html.Div(children='''
        This is our Kill Sheet App page content.
    '''),
])