import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
import pandas as pd
import dash_ag_grid as dag

# Helper Functions --------------------------------------------------
def wv_default_formatter(df):
    empty_val = '--'
    start_md = f"{df.start_md[0]}'md"
    end_md = f"{df.end_md[0]}' md"
    end_tvd = f"{df.end_tvd[0]}' tvd"
    
    puw = f'PUW= {df.puw[0]} klbs'
    sow = f'SOW= {df.sow[0]} klbs'
    rtw = f'RTW= {df.rtw[0]} klbs'
    
    rop = f"ROP= {df.rop[0]} fph"
    wob = f"WOB= {df.wob[0]} klbs"
    
    gpm = f'GPM= {df.gpm[0]} gpm'
    psi = f'SPP= {df.spp[0]} psi'
    flow_out = f'FLOW-OUT= {df.fout[0]}%'
    
    rpm = f'RPM= {df.rpm[0]} rpm'
    tq = f'TQ= {df.tq[0]} klbs'
    
    mud_wt =f'MW= {df.mw[0]} ppg'
    ecd = f'ECD= {df.ecd[0]} ppge'
    
    return f'''Drilling from {start_md} to {end_md}, {end_tvd} \r
    {puw}, {sow}, {rtw} \r
    {rop}, {wob} \r
    {gpm}, {psi}, {flow_out} \r
    {rpm}, {tq} \r
    {mud_wt}, {ecd} \r
Notes:  '''

def templater_text_output(well_name,df):
    return html.Div(children=[
        dbc.Row(children=[
            dbc.Col(dcc.Markdown(f'#### **{well_name}** - Wellview Timelog Summary')),
            dbc.Col(dcc.Clipboard(
                target_id="tempalter_text_output",
                title="Copy to Clipboard",
                style={
                    "display": "inline-block",
                    "fontSize": 20,
                    "verticalAlign": "top",
                    "float": "right",
                    "backgroundColor": "white",
                    "color": "#1864da",
                },
            ),width=2),
        ]),
        dcc.Textarea(
            id='tempalter_text_output',
            value=wv_default_formatter(df),
            spellCheck=False,   
            style={'width': '100%', 'height': '250px'},
        ),
    ],style={'margin-top': '25px'})
    
# print(wv_default_formatter())