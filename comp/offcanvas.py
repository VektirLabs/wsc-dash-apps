import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
  
def home_sidebar():
    return html.Div(
    [
        dbc.Offcanvas(
            children=[
                html.H4('WSC - Home'),
                html.H6('App Verison: 1.0.0'),
                html.H6('App Updated: 6/25/23'),
                html.H6('App Developer: Tyler Hunt'),
                html.H6('App Email: wscrigadvisor@conocophillips.com')
                ],
            id="offcanvas-home-sidebar",
            title="",
            is_open=False,
        ),
    ]
)
    
def templater_sidebar():
    return html.Div(
    [
        dbc.Offcanvas(
            children=[
                html.H4('WSC - Templater App'),
                html.Div(
                    dcc.Dropdown(
                        id='status_id',
                        options=[
                            {'label': 'Active Wells', 'value': 'A1'},
                            {'label': 'Complete Wells', 'value': 'H2'},
                        ], value='A1' 
                    ),style={'padding': '5px'}
                ),
                html.Div(
                    dcc.Dropdown(
                        id='prev_hrs_id',
                        options=[
                            {'label': 'Previous 3 hours', 'value': 3},
                            {'label': 'Previous 6 hours', 'value': 6},
                            {'label': 'Previous 9 hours', 'value': 9},
                            {'label': 'Previous 12 hours', 'value': 12},
                            {'label': 'Previous 15 hours', 'value': 15},
                            {'label': 'Previous 18 hours', 'value': 18},
                            {'label': 'Previous 21 hours', 'value': 21},
                            {'label': 'Previous 24 hours', 'value': 24},
                        ], value=3 
                    ),style={'padding': '5px'}
                ),    
                 html.Div( # todo: wire up to the formatters
                    dcc.Dropdown(
                        id='ops_type',
                        options=[
                            {'label': 'Default Formatter', 'value': 'df'},
                            {'label': 'Mud Motor Formatter', 'value': 'mmf'},
                            {'label': 'RSS Formatter', 'value': 'rf'},
                            {'label': 'RSS w/MPD Formatter', 'value': 'rmf'},

                        ], value='df' 
                    ),style={'padding': '5px'}
                ),         
                html.Div(
                    dcc.Dropdown(
                        id='well_name_id',
                        options=[{'label': 'No wells available', 'value': 'A1'}],
                        value=None,
                        placeholder='Select a well...'
                    ),style={'padding': '5px'}
                ),
               
                html.Div(
                    dbc.Button('Submit', id='submit-button', n_clicks=0, color='primary'),style={'padding': '5px'}
                ),
                ],
            id="offcanvas-templater-sidebar",
            title="",
            is_open=True,
        ),
    ]
)

def calculator_sidebar():
    btn_style = {'width': '350px', 'margin': '5px'}
    return html.Div([
        dbc.Offcanvas(
            children=[
                html.H4('WSC - Calculator Apps'),
                dbc.ButtonGroup([
                    dbc.Button("Pipe pick-up calculator", outline=True, color="primary", n_clicks=0, id="btn-calc-1",style=btn_style),
                    dbc.Button("FIT/LOT psi calculator",  outline=True, color="primary",  n_clicks=0, id="btn-calc-2", style=btn_style),
                    dbc.Button("EMW calculator",  outline=True, color="primary",  n_clicks=0, id="btn-calc-3",style=btn_style)
                    ],vertical=True,
                )
            ],
            id="offcanvas-calculator-sidebar",
            title="",
            is_open=True,
        ),
    ]
)

def template_sidebar():
    return html.Div(
    [
        dbc.Offcanvas(
            children=[
                html.H4('WSC - Template Sidebar'),
           
                ],
            id="offcanvas-template-sidebar",
            title="",
            is_open=False,
        ),
    ]
)
    