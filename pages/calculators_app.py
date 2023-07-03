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
from comp.offcanvas import calculator_sidebar
from comp.calculators import default_layout, get_pipe_pu_calc, get_emw_calc, get_fit_lot_calc

# --- Register pages ----------------------------------------------------
dash.register_page(
    __name__,
    path='/calculators_app',
    title='WSC - Calculators Apps',
    name='WSC - Calculators Apps'
)

# --- Helper functions --------------------------------------------------
def menu_btn(): 
    return html.Button(id='offcanvas_calculator_btn',n_clicks=0,
        children=[html.I(className="fa fa-angle-right"),""], 
        className="btn", 
        style={'height':'32px', 'position': 'absolute', 'left': '3px', 
               'top': '52px','color':'grey','fontSize': '24px'}
    )
 
# --- Layout ------------------------------------------------------------
layout = dcc.Loading(
    id='loading',
    type='default',
    color='#119DFF',
    children=[ 
        html.Div(children=[ 
            menu_btn(),
            calculator_sidebar(),
            html.H3(
                children=[
                    html.Img(src='https://img.icons8.com/stickers/100/calculator--v1.png', 
                            style={'height':'30px', 'margin-right':'10px'}),
                    'Calculator Apps',
                ],
            style={'margin-top': '-35px'}
            ), 
            html.Hr(),
            html.Div(id='calcs_content')
        ])
    ])

# Callbacks ----------------------------------------------------------- 
# # Calculators sidebar -----------------------------------------------
@callback(
    Output("offcanvas-calculator-sidebar", "is_open"),
    Input("offcanvas_calculator_btn", "n_clicks"),
    State("offcanvas-calculator-sidebar", "is_open"),
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Calculators ---------------------------------------------------------
@callback(
    Output("calcs_content", "children"),
    [Input("btn-calc-1", "n_clicks"),
     Input("btn-calc-2", "n_clicks"),
     Input("btn-calc-3", "n_clicks"),
     # add more if needed
    ],)
def update_layout(btn1, btn2, btn3):
    ctx = dash.callback_context
    if not ctx.triggered:
        return default_layout()
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-calc-1':
            return get_pipe_pu_calc()
        elif button_id == 'btn-calc-2':
            return get_fit_lot_calc()       
        elif button_id == 'btn-calc-3':
            return get_emw_calc()
        else: 
            return default_layout()

