import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def templator_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/3d-fluency/94/open-book--v1.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4("Templater App", className="card-title"),
                html.P(
                    "This app simplifies adding Wellview timelog and "
                    " drilling parameter entries using available data ",
                    className="card-text",
                ),
                dcc.Link( # Navigate to the Templater App
                    dbc.Button("Templater App", id='btn_templater_app' ,outline=True, color="primary"),
                    href='/templater_app'
                )
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)

def interpolator_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/dotty/80/coordinate-system.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4("Interpolator App", className="card-title"),
                html.P(
                    "This app simplifies survey file interpolation. "
                    " Note: This app is still under development ",
                    className="card-text",
                ),
                dcc.Link(
                dbc.Button("Interpolator App", outline=True, color="primary"),
                href='/interpolator_app'
                )
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)

def freeze_protect_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/color/96/iceberg.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4("Freeze Protect App", className="card-title"),
                html.P(
                    "This app simplifies the Freeze Protection calculations. "
                    " Note: This app is still under development ",
                    className="card-text",
                ),
                dcc.Link(
                    dbc.Button("Freeze Protect App", outline=True, color="primary"),
                    href='/freeze_protect_app'
                )
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)

def calculator_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/stickers/100/calculator--v1.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4("Calculators App", className="card-title"),
                html.P(
                    "This app is a collection of common D&W calculators. "
                    " Note: This app is still under development ",
                    className="card-text",
                ),
                dcc.Link(
                    dbc.Button("Calculators App", outline=True, color="primary"),
                    href='/calculator_app')
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)
    
def analysis_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/color/100/combo-chart--v1.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4("Analysis Apps", className="card-title"),
                html.P(
                    "This app is a collection of dynamic data projects. "
                    " Note: This app is still under development ",
                    className="card-text",
                ),
                dcc.Link(
                    dbc.Button("Analysis App", outline=True, color="primary"),
                    href='/analysis_app')
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)

def killsheet_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/officel/100/pressure.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4("Kill Sheet App", className="card-title"),
                html.P(
                    "This is the Kill sheet app for well control "
                    " Note: This app is still under development ",
                    className="card-text",
                ),
                dcc.Link(
                    dbc.Button("Kill Sheet App", outline=True, color="primary"),
                    href='/killsheet_app')
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
    )
    
def tallyblaster_card(name='Tally Blaster'):
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/external-chloe-kerismaker/100/external-Cannon-carnival-chloe-kerismaker.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),
        dbc.CardBody(
            [
                html.H4(f"{name} App", className="card-title"),
                html.P(
                    f"The {name} app is an app for managing tallies  "
                    " Note: This app is still under development ",
                    className="card-text",
                ),
                dcc.Link(
                    dbc.Button(f"{name} App", outline=True, color="primary"),
                    href=f'/tallyblaster_app')
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)

def default_card():
    return dbc.Card(
    [
        dbc.CardImg(src="https://img.icons8.com/color/96/work.png", top=True,
                     style={"height": "100px", "width": "100px"},
                     className="mx-auto d-block"),

        dbc.CardBody(
            [
                html.H4("Work in Progress", className="card-title"),
                html.P(
                    "Some quick example text to build on the card title and "
                    "make up the bulk of the card's content.",
                    className="card-text",
                ),
                dcc.Link(
                    dbc.Button("Come back later",outline=True, disabled=True, color="primary"),
                    href='/error404'
                )
            ]
        ),
    ],
    style={"width": "18rem"}, className="m-4",
)
