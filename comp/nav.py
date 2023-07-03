import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

navbar = dbc.NavbarSimple(
    children=[
        html.Div(html.H3('Well Support Center',
            style={'color': 'white', 'fontWeight': 'bold',  'position': 'absolute', 'left': '75px', 'top': '12px'}),),
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Templater App", href="/templater_app"),
                dbc.DropdownMenuItem("Interpolator App", href="/interpolator_app"),
                dbc.DropdownMenuItem("Freeze Protect App", href="/freeze_protect_app"),
                dbc.DropdownMenuItem("Calculators App", href="/calculators_app"),
                dbc.DropdownMenuItem("Analysis App", href="/analysis_app"),
                dbc.DropdownMenuItem("Kill Sheet App", href="/killsheet_app"),
                dbc.DropdownMenuItem("Tally Blaster App", href="/tallyblaster_app"),
             
            ],
            nav=True,
            in_navbar=True,
            label="More Apps",
        ),
    ],
    brand_href="#",
    color="primary",
    dark=True,
    sticky = 'top'
    
)