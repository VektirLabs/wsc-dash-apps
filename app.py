import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output, State
from comp import nav, body, offcanvas, modal
from utils.helpers import * # see helpers for details

# Globals -----------------------------------------------------------

# App setup ---------------------------------------------------------
app = Dash(
    __name__, 
    use_pages=True,
    external_stylesheets=[dbc.themes.COSMO,dbc.icons.FONT_AWESOME]
    )

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    home_menu_btn(),
    offcanvas.home_sidebar(), 
    nav.navbar, 
    body.main, 
    ])

# Callbacks ---------------------------------------------------------
# # Home Sidebar -----------------------------------------------
@callback(
    Output("offcanvas-home-sidebar", "is_open"),
    Input("offcanvas_home_btn", "n_clicks"),
    State("offcanvas-home-sidebar", "is_open"),
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Main --------------------------------------------------------------
if __name__ == '__main__':
	app.run_server(debug=True)