import dash
from dash import html, dcc

dash.register_page(
    __name__,
    path='/interpolator_app',
    title='WSC - Interpolator App',
    name='WSC - Interpolator App'
)

layout = html.Div(children=[
    html.H1(children='Interpolator App'),

    html.Div(children='''
        This is our Interpolator App page content.
    '''),
])