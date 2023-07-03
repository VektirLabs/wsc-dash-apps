import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
import pandas as pd
import dash_ag_grid as dag

# # Globals ---------------------------------------------------------
columnDefs  = [{'field': 'Name', 'editable': False},{'field': 'Input', 'editable': True},]
  
def default_layout():
    return html.Div([
        html.H1('Default layout'),
    ])

def get_pipe_pu_calc():
    return html.Div([
        html.H1('Pipe pick-up calculator'),
    ])
    
def get_fit_lot_calc():
    return html.Div([
        html.H1('FIT or LOT calculator'),
        dcc.Markdown('''### Formation Test Pressure
                     $$
                     FTp = (Test MW - Original MW) * 0.052 * (Tvd at Shoe)
                     $$ 
                     ''', mathjax=True),
        # TODO: play with this aggrid more
        
        dag.AgGrid(
            id="column-definitions-basic",
            rowData=[{"Name": "Test mud wt.",
                    "Input": 15.0,},
                    {"Name": "Original mud wt.",
                    "Input": 1000,},
                    {"Name": "Tvd at Shoe",
                    "Input": 2500,},
            ],
            defaultColDef={"resizable": False, "sortable": False, "filter": False},

            columnDefs=[{'field': 'Name', 'editable': False} , 
                        {'field': 'Input', 'editable': True,
                            "valueFormatter": {"function": """d3.format("(,.2f")(params.value)"""}}, 
                        ],
            columnSize="sizeToFit",
            style={"height": 200, "width": 350}
        ),
        
    ])
    
def get_emw_calc():
    return html.Div([
        html.H1('Emw calculator'),
    ])