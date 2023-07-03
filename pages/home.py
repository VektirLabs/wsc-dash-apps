import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from comp import cards

dash.register_page(__name__, path='/')
# https://icons8.com/icons/set
# Rig Icon - https://img.icons8.com/external-beshi-flat-kerismaker/96/external-Drilling-Rig-industry-beshi-flat-kerismaker.png

templater_card = cards.templator_card()
interpolator_card = cards.interpolator_card()
freeze_protect_card = cards.freeze_protect_card()
calculator_card = cards.calculator_card()
analysis_card = cards.analysis_card()
killsheet_card  = cards.killsheet_card()
tallyblaster_card  = cards.tallyblaster_card()
default_card = cards.default_card()

# Layout ------------------------------------------------------------
layout = html.Div(
    children=[
        html.H3(
                children=[
                    html.Img(src='https://img.icons8.com/fluency/100/home.png', 
                             style={'height':'40px', 'margin-right':'10px'}),
                    'Well Support Center Apps',
                ],
            style={'margin-top': '-35px'}
            ), 
        dbc.Row(html.Caption(children='Welcome to the WSC Operations Apps Home Page')),
        html.Hr(),
        html.Div([
            dbc.Row([
                dbc.Col(templater_card),
                dbc.Col(interpolator_card),
                dbc.Col(freeze_protect_card),
                dbc.Col(calculator_card),
                dbc.Col(analysis_card),
                dbc.Col(killsheet_card),
                dbc.Col(tallyblaster_card),
                dbc.Col(default_card),
                dbc.Col(default_card),
            ]),
        ]),        
    ],style={'margin-right': '50px'})

# callbacks ---------------------------------------------------------

