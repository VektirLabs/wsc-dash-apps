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
    path='/template_page',
    title='WSC - Template Page',
    name='WSC - Template Page'
)

# --- Helper functions ----------------------------------------------
def menu_btn(): 
    return html.Button(id='offcanvas_templater_btn',n_clicks=0,
        children=[html.I(className="fa fa-angle-right"),""], 
        className="btn", 
        style={'height':'32px', 'position': 'absolute', 'left': '3px', 'top': '52px','color':'grey','fontSize': '24px'}
    )

# --- Layout --------------------------------------------------------
layout = dcc.Loading(
    id='loading',
    type='default',
    color='#119DFF',
    children=[ 
        html.Div(children=[ 
            # menu_btn(),
            # templater_sidebar(),
            html.H3(
                children=[
                    html.Img(src='https://img.icons8.com/3d-fluency/94/open-book--v1.png', 
                            style={'height':'30px', 'margin-right':'10px'}),
                    'Templater App',
                ],
            style={'margin-top': '-35px'}
            ), 
            html.Hr(),
        ])
    ])

# --- Callbacks -----------------------------------------------------

# # Sidebar -----------------------------------------------
@callback(
    Output("offcanvas-xxx-sidebar", "is_open"),
    Input("offcanvas_xxx_btn", "n_clicks"),
    State("offcanvas-xxx-sidebar", "is_open"),
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open
