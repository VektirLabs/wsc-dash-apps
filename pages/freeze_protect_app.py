import dash
from dash import html, dcc

dash.register_page(
    __name__,
    path='/freeze_protect_app',
    title='WSC - Freeze Protect App',
    name='WSC - Freeze Protect App'
)

layout = html.Div(children=[
    html.H1(children='Freeze Protect App'),

    html.Div(children='''
        This is our Freeze Protect page content.
    '''),
])