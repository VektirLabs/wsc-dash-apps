import dash
from dash import html, dcc

dash.register_page(__name__, path='/error404')

layout = html.Div(children=[
    html.H1(children='This is our 404 page'),

    html.Div(children='''
        This is our 404 page content.
    '''),
])