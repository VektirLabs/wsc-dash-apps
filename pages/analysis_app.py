import dash
from dash import html, dcc

dash.register_page(
    __name__,
    path='/analysis_app',
    title='WSC - Analysis App',
    name='WSC - Analysis App'
)

layout = html.Div(children=[
    html.H1(children='Analysis App'),

    html.Div(children='''
        This is our Analysis App page content.
    '''),
])