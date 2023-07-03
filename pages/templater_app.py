import dash
from datetime import datetime
from dash import html, dcc
import dash_bootstrap_components as dbc
from utils import con_corva as cc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from dash import exceptions as e
from comp.offcanvas import templater_sidebar #sidebar
from comp.text_output import templater_text_output
from dash.exceptions import PreventUpdate
from utils.con_corva import get_telemetry_data_by_id_date_range
from utils.helpers import * # see helpers for details

# --- Register pages ------------------------------------------------
dash.register_page(
    __name__,
    path='/templater_app',
    title='WSC - Templater App',
    name='WSC - Templater App'
)

# --- Layout --------------------------------------------------------
layout = dcc.Loading(
    id='loading',
    type='default',
    color='#119DFF',
    children=[ 
        html.Div(children=[ 
            templater_menu_btn(),
            templater_sidebar(),
            # dcc.Storage for storing data from the corva api 
            dcc.Store(id='session_store', storage_type='session'),      # data store - df_wits - session
            dcc.Store(id='well_name_store'),        # data store - well name id - session
            dcc.Store(id='click_store'),            # data store - click data - session
            dcc.Store(id='load_hours'),             # data store - load hours - session
            dcc.Store(id='well_status_store'),      # data store - well status data - session
            
            # --- Header name and Hr --------------------------------
            html.H3(
                children=[
                    html.Img(src='https://img.icons8.com/3d-fluency/94/open-book--v1.png', 
                            style={'height':'30px', 'margin-right':'10px'}),
                    'Templater App',
                ],
            style={'margin-top': '-35px'}
            ), 
            html.Hr(),
          
            # --- Header graph section ------------------------------
                dbc.Row([
                        dbc.Col([
                            html.P(id='grp_output',style={'textAlign': 'center','color': 'black','fontSize': 24,}),
                            dcc.Graph(
                                id='grp_ops', 
                                selectedData=None, 
                                style={'height': '200px'}
                                )               
                        ], style={'text-align': 'left', "marginRight": "10px"}, id="dummy-input", md=12)
                    ]),
                dbc.Row(html.Hr()),  
            
            # --- Lower output section ------------------------------
                dbc.Row(children=[
                    
                    # --- Drilling timelog sumamry ------------------
                    dbc.Col(children=[
                        html.Div(id='hidden_text')   ,
                        html.Div(id='templater_text_area')    
                    ]),
                    
                    # --- Drilling parameters sumamry -------------             
                    dbc.Col(children=[
                        # dcc.Markdown('''#### Parameter Summary''',style={'text-align':'center'}),
                        html.Div(id='templater_parameter_area')    
                    ]),
                ])

            
            ], style={'margin-right': '50px'})
    ])

# --- Callbacks -----------------------------------------------------

# # Retrieve wells list from Corva ----------------------------------
@callback(
    Output('well_name_id', 'options'),[
    Input('dummy-input', 'children'),
    Input('status_id', 'value') 
    ])
def update_dropdown(dummy, status_id):
    """
        Input: dummy, status_id
        Output: options to the well_name_id dropdown
    """
    # Fetch the data
    df = cc.get_header_data()
    
    # If the DataFrame is empty, return the initial options
    if df.empty:
        return [{'label': 'No wells available', 'value': 'A1'}]
    
    # Get unique values from the DataFrame column
    wells_list = df['name'].unique()
    
    if status_id == 'A1':
        # Filter the unique values to only include active wells
        wells_list = df.query('status == "active"')['name'].unique()
    elif status_id == "H2":
        # Filter the unique values to only include complete wells
        wells_list = df.query('status == "complete"')['name'].unique()
    else:
        wells_list = df['name'].unique()
        
    # Convert the unique values to dropdown options
    options = [{'label': value, 'value': value} for value in wells_list]
    
    return options

# # Retrieve wits data Callback ->Header Graph  ---------------------
@callback(
    Output('session_store', 'data'),
    [Input('well_name_store', 'data'),
     Input('load_hours', 'data')],)
def update_data(well_name_store, load_hours):

    ctx = dash.callback_context

    if not ctx.triggered:
        raise e.PreventUpdate

    if well_name_store is None or load_hours is None:
        raise e.PreventUpdate

    # Fetch data from Corva API and store in session
    asset_id = get_header_id_by_name(well_name=well_name_store)
    df_wits = cc.get_telemetry_overview_data_by_id(int(asset_id), hrs=load_hours)

    # Convert 'time_stamp' column to datetime if it's not already
    df_wits['time_stamp'] = pd.to_datetime(df_wits['time_stamp'])

    # Return session_store data and None for the other stores to clear them
    return df_wits.to_dict()

# # Retrieve wits date range data -> Hidden   -----------------------
@callback(
    Output('hidden_text', 'children'),
    [Input('well_name_store', 'data'),
     Input('click_store', 'data')],
    prevent_initial_call=True)
def update_data(name, click_data):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Return early if the click_data is not valid
    if click_data is None or input_id != 'click_store':
        raise PreventUpdate
    
    start_time = click_data["start"]
    end_time = click_data["end"]
    asset_id = get_header_id_by_name(name)
    
    df_wits = get_telemetry_data_by_id_date_range(asset_id, start_time, end_time)

    df_wits_std_cntr = add_stand_counter_logic(df_wits)
    df_wits_prepd = prep_df_wits_data(df_wits_std_cntr)

    # Update the hidden_text children with name and click data
    return f'Name: {name}, Start Time: {click_data["start"]}, End Time: {click_data["end"]}'

# # Store Query Callback -------------------------------------------
@callback(
    [Output('well_name_store', 'data'),
     Output('load_hours', 'data')],
    [Input('submit-button', 'n_clicks')],
    [State('well_name_id', 'value'),
     State('prev_hrs_id', 'value')],
    prevent_initial_call=True)
def store_query_data(n_clicks, well_name_id, prev_hrs_id):
    if n_clicks is None:
        raise e.PreventUpdate

    # Returning the well name and load hours to the corresponding stores
    return well_name_id, prev_hrs_id

# # Header Graph Callback -------------------------------------------
@callback(
    [Output('grp_ops', 'figure'),
     Output('grp_output','children')],
    [Input('dummy-input', 'children'),
     Input('click_store', 'data'), 
     Input('session_store', 'data'),
     Input('well_name_store', 'data')],
    [State('grp_ops', 'figure')])
def update_graph(dummy, click_data, session_data, well_id, existing_figure):
    temp_fig = go.Figure()
    temp_fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date",
                gridcolor='rgba(202, 202, 202, 0.5)'
            ),
            yaxis=dict(
                autorange='reversed',
                gridcolor='rgba(202, 202, 202, 0.5)'
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height = 200,
            margin=dict(l=20, r=20, t=5, b=5),
        )
        
    # Check if well_id is None
    if well_id is None:
        return temp_fig, ''
    
    # Check if there is any data in the session_store
    if session_data is None:
        return temp_fig, ''

    # Load data from session_store
    df = pd.DataFrame(session_data)
    
    # Create figure
    fig = go.Figure()
    
    hover_labels = f'''Well name: {well_id} 
                    <br> Date time: %{{x}}
                    <br> Block height: %{{y:.0f}}
                    <br> Bit depth: %{{customdata[0]:.0f}}
                    <br> Hole depth: %{{customdata[1]:.0f}}
                <extra></extra>'''
    

   # Create separate dataframes for each condition
    df_state_drill_0 = df[df['state_drill'] == 0]
    df_state_drill_1 = df[df['state_drill'] == 1]

   # All Block height trace
    fig.add_trace(
        go.Scatter(
            x=list(df.time_stamp),
            y=list(df.block_height),
            mode='lines', 
            line=dict(color="rgba(125, 125, 125, 0.50)", width=4), 
            hovertemplate=hover_labels,
            name="Block Height",
            customdata=df[['bit_depth', 'hole_depth']]
        )
    )

    # Block height trace for off bottom
    fig.add_trace(
        go.Scatter(
            x=list(df_state_drill_0.time_stamp),
            y=list(df_state_drill_0.block_height),
            mode='markers', 
            marker=dict(size=3, color="rgba(75, 75, 75, 0.0)"),  
            hovertemplate=hover_labels,
            name="Off Bottom",
            customdata=df_state_drill_0[['bit_depth', 'hole_depth']]
        )
    )

    # Block height trace for on bottom
    fig.add_trace(
        go.Scatter(
            x=list(df_state_drill_1.time_stamp),
            y=list(df_state_drill_1.block_height),
            mode='markers',
            marker=dict(size=3, color="rgba(24, 74, 223, 0.8)"),  
            hovertemplate=hover_labels,
            name="On Bottom",
            customdata=df_state_drill_1[['bit_depth', 'hole_depth']]
        )
    )

  
    # Add range slider
    fig.update_layout(
        dragmode='select', 
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date",
            gridcolor='rgba(202, 202, 202, 0.5)'
        ),
        yaxis=dict(
            # autorange='reversed',
            gridcolor='rgba(202, 202, 202, 0.5)'
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height = 200,
        margin=dict(l=20, r=20, t=5, b=5),
        showlegend=True,
    )
    
    if click_data is not None and 'start' in click_data and 'end' in click_data:
        start = click_data['start']
        end = click_data['end']
        
        fig.add_shape(
            # Line Vertical
            dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=start,
                y0=0,
                x1=end,
                y1=1,
                fillcolor="LightSkyBlue",
                opacity=0.25,
                layer="below",
                line_width=0,
            )
        )
    
  # Get the latest datetime
    time_max = np.max(df["time_stamp"])

    # Ensure it's a datetime object
    if isinstance(time_max, str):
        time_max = datetime.strptime(time_max, "%Y-%m-%dT%H:%M:%S")

    # Format the datetime object
    formatted_time_max = time_max.strftime("%m/%d/%Y %H:%M")

    well_label = ""
    if well_id is not None:
        well_label = f'Well: {well_id} - Date: {formatted_time_max}'
        
    return fig, well_label

# # Store/clear selected data ---------------------------------------------
@callback(
    Output('click_store', 'data'),
    [Input('grp_ops', 'selectedData'),
     Input('well_name_id', 'value')])
def manage_store_data(selected_data, dropdown_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if input_id == 'grp_ops':
        if selected_data is not None and 'range' in selected_data:
            range = selected_data['range']['x']
            start = range[0]
            end = range[1]
            return {'start': start, 'end': end}
        else:
            return dash.no_update
    elif input_id == 'well_name_id':
        return None

# # Templater Textarea ----------------------------------------------
@callback(
    Output('templater_text_area', 'children'),
    [Input('click_store', 'data'),
     Input('well_name_store', 'data')])
def update_text_area(click_data, well_name_store):
    ctx = dash.callback_context
    df_str = pd.DataFrame()
    
    if not ctx.triggered:
        trigger_id = 'No clicks yet'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'click_store' and click_data is not None and 'end' in click_data:
        start = click_data['start']
        end = click_data['end']
        if well_name_store is not None:
            asset_id = get_header_id_by_name(well_name_store)
            df_str = get_telemetry_data_by_id_date_range(asset_id=asset_id, start=start,end=end)
            df = prep_df_wits_data(df_str)
        
        return html.Div([
            templater_text_output(
                well_name=well_name_store
                , df=df
                )
        ])
    else:
        return html.Div('')  

# # Templater sidebar -----------------------------------------------
@callback(
    Output("offcanvas-templater-sidebar", "is_open"),
    Input("offcanvas_templater_btn", "n_clicks"),
    State("offcanvas-templater-sidebar", "is_open"),)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


