from utils import con_corva as cc
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import pandas as pd

# --- Helper functions ----------------------------------------------
def get_header_id_by_name(well_name):
    ASSET = ''
    
    # Get header df
    df = cc.get_header_data()
    
    # Clean df
    search_items = ['(',')', 'delete','Benchmark']
    c_df = df[~df['name'].apply(lambda x: any(item in x for item in search_items))]

    #Search df
    ASSET = c_df[c_df['name'] == well_name]['asset_id'].to_list()[0]
    
    return ASSET 

def home_menu_btn(): 
    return html.Button(id='offcanvas_home_btn',n_clicks=0,
        children=[html.I(className="fa fa-angle-right"),""], 
        className="btn", 
        style={'height':'32px', 'position': 'absolute', 'left': '3px',
               'top': '52px','color':'grey','fontSize': '24px'}
    )
    
def templater_menu_btn(): 
    return html.Button(id='offcanvas_templater_btn',n_clicks=0,
        children=[html.I(className="fa fa-angle-right"),""], 
        className="btn", 
        style={'height':'32px', 'position': 'absolute', 'left': '3px', 'top': '52px','color':'grey','fontSize': '24px'}
    )

#todo not being used
def get_timelog_summary_data(df, start, end):
  # Clean up df - convert dt & filter
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
  
    filter_mask = (df['time_stamp'] >= start) & (df['time_stamp'] <= end)
    df = df.loc[filter_mask]
    # todo get raw telemetry from Corva
    return str(df.to_dict())

def prep_df_wits_data(df_wits):
    df_out = pd.DataFrame()
    
    # filter to only drilling on bottom data
    df_wits_on_btm = df_wits[df_wits['state_drill'] == 1].copy()
    df_wits_off_btm = df_wits[df_wits['state_drill'] == 0].copy()

    if df_wits is None:
        return df_out
    
    start_md = np.round(np.min(df_wits_on_btm['hole_depth']),0)
    end_md = np.round(np.max(df_wits_on_btm['hole_depth']),0)
    end_tvd = '--' #np.round(np.max(df_wits_on_btm['tvd']),0)
    
    # TODO:Need to get from T&D info
    puw = '--' #np.round(np.max(df_wits['hookload']),0)
    sow = '--' #np.round(np.max(df_wits['hookload']),0)
    rtw = '--' #np.round(np.max(df_wits['hookload']),0)
    
    rop = np.round(np.average(df_wits_on_btm['rop']),0)
    wob = np.round(np.average(df_wits_on_btm['weight_on_bit']),2)
    
    gpm = np.round(np.average(df_wits_on_btm['mud_flow_in']),0)
    spp = np.round(np.average(df_wits_on_btm['standpipe_pressure']),0)
    fout = np.round(np.average(df_wits_on_btm['mud_flow_out_percent']),0)
    rpm = np.round(np.average(df_wits_on_btm['rotary_rpm']),0)
    tq = np.round(np.average(df_wits_on_btm['rotary_torque']),1)
    
    mw = np.round(np.average(df_wits_on_btm['mwd_annulus_ecd']),2)
    ecd = np.round(np.average(df_wits_on_btm['mwd_annulus_ecd']),2)
    
    df_out = pd.DataFrame([
        {'start_md': str(start_md),
         'end_md': str(end_md),
         'end_tvd': str(end_tvd),
         'puw': str(puw),
         "sow": str(sow),
         'rtw': str(rtw),
         'rop': str(rop),
         'wob': str(wob),
         'gpm': str(gpm),
         'spp': str(spp),
         'fout': str(fout),
         'rpm': str(rpm),
         'tq': str(tq),
         'mw':str(mw),
         'ecd': str(ecd),
        }
    ])
    print(df_out.reset_index(drop=True))
    return df_out.reset_index(drop=True)
    
def add_stand_counter_logic(df_wits):
    df_orig = df_wits.copy()
    df_out = pd.DataFrame()

    df_orig['bh_deriv'] = df_orig['block_height'].diff()

    df = df_orig[df_orig['bottom_status'] == "near_bottom"]

    # Assume 'time_stamp' is the datetime index
    df.set_index('time_stamp', inplace=True)

    # Resample to 15-minute windows and get max value
    df_resampled = df['bh_deriv'].resample('30S').max()
    threshold = df_resampled.std() * 7.5
    df_resampled = df_resampled.reset_index()
    df_resampled.columns = ['time_stamp', 'bh_deriv']
    df_resampled['threshold'] = threshold
    df_resampled['is_Conn'] = df_resampled['bh_deriv'].where(df_resampled['bh_deriv'] > threshold)

    df_resampled = df_resampled[df_resampled['is_Conn'].notna()]
    df_resampled['std_num'] = df_resampled.reset_index().index +1

    df_conns = df_resampled[['bh_deriv','std_num']]

    df_out = df_orig.merge(df_conns, left_on='bh_deriv', right_on='bh_deriv', how='left')
    df_out['std_num'] = df_out['std_num'].fillna(method='ffill').fillna(0).astype(int)
    
    return df_out