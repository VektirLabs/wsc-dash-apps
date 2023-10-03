import requests
import json
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import numpy as np
import pytz
load_dotenv()  

def convert_time_range_to_unix_timestamp(start, end, timezone="America/Anchorage", format="%Y-%m-%d %H:%M:%S.%f"):
    local_tz = pytz.timezone(timezone)
    
    dt_start = datetime.strptime(start, format)
    dt_start = local_tz.localize(dt_start)
    dt_start = dt_start.astimezone(pytz.UTC)

    dt_end = datetime.strptime(end, format)
    dt_end = local_tz.localize(dt_end)
    dt_end = dt_end.astimezone(pytz.UTC)

    return int(dt_start.timestamp()), int(dt_end.timestamp())  

def get_header_data() -> pd.DataFrame():
    url ='https://api.corva.ai/v1/data/corva/assets'
    auth = {'Authorization': os.getenv('API_KEY')}

    params = {"sort": '{timestamp: 1}',
            "query": "{county#eq#'Alaska'}",
            "limit":"inf"
            }

    try:
        r = requests.get(url, params=params, headers=auth)
        result = json.loads(r.text)
        df = pd.DataFrame.from_records(result)
        df = df.loc[([True if i['name']=='Alaska' else False for i in df['program']])]
        
        # Clean df
        search_items = ['(',')', 'delete','Benchmark']
        c_df = df[~df['name'].apply(lambda x: any(item in x for item in search_items))]
        c_df = c_df.sort_values('name', ascending=True)
        
        return c_df
    
    except requests.exceptions.RequestException as e:
        print(f"Error 1: {e}")
        return pd.DataFrame()

    except json.JSONDecodeError as e:
        print(f"Error 2: {e}")
        return pd.DataFrame()

    except Exception as e:
        print(f"Error 3: {e}")
        return pd.DataFrame()
    
def get_telemetry_data_by_list(assets) -> pd.DataFrame():
    url = f'https://api.corva.ai/v1/data/corva/wits.summary-1m?'
    auth = {'Authorization':os.getenv('API_KEY')}
    telem_fields ="""timestamp, data.bit_depth, data.block_height, data.hole_depth, 
    data.hook_load, data.rotary_rpm, data.rotary_torque, 
    data.pump_spm_1, data.pump_spm_2, data.pump_spm_total, data.standpipe_pressure, 
    data.mud_flow_in, data.strks_total,data.gain_loss, 
    data.mwd_annulus_ecd, data.mud_flow_out_percent, data.state
    """

    # Get active well asset ids
    df_active_headers = get_header_data()
    active_assets = df_active_headers['asset_id'].to_list()
    active_well_name = df_active_headers['name'].to_list()
    active_rig_name = df_active_headers['rig'].apply(lambda x: x['name']).to_list()
    
    # loop through assets and get last 24 hours of telemetry data
    df_wits = pd.DataFrame()
    for i, id in enumerate(assets):
        params = {"asset_id": id,
          "sort": '{timestamp: 1}',
          "fields": telem_fields,
          "limit":"1"
        }

        try:
            # Request corva data
            r = requests.get(url, params=params, headers=auth)
            js = r.json()
            
            # Append a data to single df_wits
            df_wits_asset = pd.DataFrame.from_records(js)  
            df_wits_asset['timeStamp'] = df_wits_asset['timestamp'].apply(lambda x:datetime.fromtimestamp(x))
            df_wits_asset = pd.concat([df_wits_asset[['timestamp','timeStamp']],pd.DataFrame.from_records(df_wits_asset['data'])],  axis=1)
            
            # Add asset info to each row
            df_wits_asset['asset_id'] = active_assets[i]
            df_wits_asset['well_name'] = active_well_name[i]
            df_wits_asset['rig_name'] = active_rig_name[i]
            
            # Append to overall dataframe
            df_wits = pd.concat([df_wits, df_wits_asset])  

        except requests.exceptions.RequestException as e:
            print(f"Error 1: {e}")
            continue

        except json.JSONDecodeError as e:
            print(f"Error 2: {e}")
            continue

        except Exception as e:
            print(f"Error 3: {e}")
            continue

    # print(df_wits.columns)
    return df_wits

def get_telemetry_data_by_id(asset_id) -> pd.DataFrame():
    url = f'https://api.corva.ai/v1/data/corva/wits?'
    auth = {'Authorization':os.getenv('API_KEY')}
    telem_fields ="""timestamp, data.bit_depth, data.block_height, data.hole_depth, data.tvd, 
    data.hook_load, data.rotary_rpm, data.rotary_torque, 
    data.pump_spm_1, data.pump_spm_2, data.pump_spm_total, data.standpipe_pressure, 
    data.mud_flow_in, data.strks_total, data.gain_loss, 
    data.mwd_annulus_ecd, data.mud_flow_out_percent, data.state, data.rigtime
    """
    
    df_wits = pd.DataFrame()
    
    # Get well asset ids
    df_headers = get_header_data()
   
    params = {"asset_id": asset_id,
        "sort": '{timestamp: -1}',
        "fields": telem_fields,
        "limit":"86400",
    }

    try:
        # Request corva data
        r = requests.get(url, params=params, headers=auth)
        js = r.json()
        
        # Append a data to single df_wits
        df_wits = pd.DataFrame.from_records(js)  
        df_wits['time_stamp'] = df_wits['timestamp'].apply(lambda x:datetime.fromtimestamp(x))
        df_wits = pd.concat([df_wits[['timestamp','time_stamp']], pd.DataFrame.from_records(df_wits['data'])], axis=1)
        
        # Add asset, well, rig info to the dataframe
        df_wits['asset_id'] = str(asset_id)
        df_wits['well_name'] = df_headers[df_headers['asset_id'] == asset_id]['name'].to_list()[0].split(' ')[0]
        df_wits['rig_name'] = df_headers[df_headers['asset_id'] ==  asset_id]['rig'].apply(lambda x: x['name']).to_list()[0]

    except requests.exceptions.RequestException as e:
        print(f"Error 1: {e}")

    except json.JSONDecodeError as e:
        print(f"Error 2: {e}")

    except Exception as e:
        print(f"Error 3: {e}")

    return df_wits

def get_telemetry_overview_data_by_id(asset_id, hrs=3) -> pd.DataFrame():
    url = f'https://api.corva.ai/v1/data/corva/wits?'
    # url = f'https://api.corva.ai/v1/data/corva/wits.summary-30s?'
    # url = f'https://api.corva.ai/v1/data/corva/wits.summary-1m?'
    auth = {'Authorization':os.getenv('API_KEY')}
    telem_fields ="""timestamp, data.bit_depth, data.block_height, data.hole_depth, data.state"""
    
    # Get well asset ids and df_wits
    df_wits = pd.DataFrame()
    df_headers = get_header_data()
 
    hrs_conv = 3600
    params = {"asset_id": asset_id,
        "sort": '{timestamp: -1}',
        "fields": telem_fields,
        "limit":f"{hrs * hrs_conv}" 
    }

    try:
        # Request corva data
        r = requests.get(url, params=params, headers=auth)
        js = r.json()

        # Append a data to single df_wits
        df_wits = pd.DataFrame.from_records(js)  
        df_wits['time_stamp'] = df_wits['timestamp'].apply(lambda x:datetime.fromtimestamp(x))
        df_wits = pd.concat([df_wits[['timestamp','time_stamp']], pd.DataFrame.from_records(df_wits['data'])], axis=1)
        df_wits['state_drill'] = df_wits['state'].str.contains('Drilling', case=False).astype(int)


        # # Add asset, well, rig info to the dataframe
        df_wits['asset_id'] = str(asset_id)
        df_wits['well_name'] = df_headers[df_headers['asset_id'] == asset_id]['name'].to_list()[0].split(' ')[0]
        df_wits['rig_name'] = df_headers[df_headers['asset_id'] ==  asset_id]['rig'].apply(lambda x: x['name']).to_list()[0]
        
        # Make sure the timestamp is a DateTimeIndex
        df_wits.set_index('time_stamp', inplace=True)
        
        # Resample to 10-second intervals 
        # todo: not sure if this is the best way to do this
        df_wits = df_wits.resample('10S').agg(
            {col: 'mean' if df_wits[col].dtype in ['float64', 'int64'] else lambda x: x.value_counts().index[0] for col in df_wits.columns})
        df_wits = df_wits.reset_index()
        
    except requests.exceptions.RequestException as e:
        print(f"Error 1: {e}")

    except json.JSONDecodeError as e:
        print(f"Error 2: {e}")

    except Exception as e:
        print(f"Error 3: {e}")

    return df_wits

def get_telemetry_data_by_id_date_range(asset_id, start, end) -> pd.DataFrame():
    url = f'https://api.corva.ai/v1/data/corva/wits?'
    auth = {'Authorization':os.getenv('API_KEY')}
    telem_fields ="""timestamp, data.bit_depth, data.block_height, 
    data.hole_depth, data.hook_load, data.rotary_rpm, data.rotary_torque, 
    data.tvd, data.pump_spm_total, data.standpipe_pressure, data.mud_flow_in, 
    data.mud_flow_in, data.rop, data.weight_on_bit, data.mwd_annulus_ecd, 
    data.mud_flow_out_percent, data.state, data.rigtime, data.mud_density
    """
    
    df_wits = pd.DataFrame()
    
    # Get well asset ids
    df_headers = get_header_data()
    
   # Format timestampes to unix int ranges
    unix_start_ts, unix_end_ts = convert_time_range_to_unix_timestamp(start=start, end=end)
    
    params = {"asset_id": asset_id,
        "sort": '{timestamp: -1}',
        "fields": telem_fields,
        "limit":"inf",
        "query": '{timestamp#gte#'+str(unix_start_ts)+ '}AND{timestamp#lte#'+str(unix_end_ts)+'}'
    }

    try:
        # Request corva data
        r = requests.get(url, params=params, headers=auth)
        js = r.json()
        
        # Append a data to single df_wits
        df_wits = pd.DataFrame.from_records(js)  
        df_wits['time_stamp'] = df_wits['timestamp'].apply(lambda x:datetime.fromtimestamp(x))
        df_wits = pd.concat([df_wits[['timestamp','time_stamp']], pd.DataFrame.from_records(df_wits['data'])], axis=1)
       
        df_wits['state_drill'] = df_wits['state'].str.contains('Drilling', case=False).astype(int)
        df_wits['bottom_status'] = np.where((df_wits['hole_depth'] - df_wits['bit_depth']) > 190, "off_bottom", "near_bottom")

        # Add asset, well, rig info to the dataframe
        df_wits['asset_id'] = str(asset_id)
        df_wits['well_name'] = df_headers[df_headers['asset_id'] == asset_id]['name'].to_list()[0].split(' ')[0]
        df_wits['rig_name'] = df_headers[df_headers['asset_id'] ==  asset_id]['rig'].apply(lambda x: x['name']).to_list()[0]
        
        # print(df_wits.columns)
    except requests.exceptions.RequestException as e:
        print(f"Error 1: {e}")

    except json.JSONDecodeError as e:
        print(f"Error 2: {e}")

    except Exception as e:
        print(f"Error 3: {e}")

    return df_wits




## Test -------------------------------------------------------------       
# # Get active well asset ids
# df_active_headers = get_header_data()
# active_assets = df_active_headers['asset_id'].to_list()

# # Get active well telemetry by asset id
# df_active_telemtry = get_telemetry_data(active_assets)

# print(df_active_headers)
# print(df_active_telemtry.columns)

# historical_assets = get_header_historical_data()
# search_items = ['(',')', 'delete','Benchmark']
# df = historical_assets[~historical_assets['name'].apply(lambda x: any(item in x for item in search_items))]

# print(df)
# start_time = time.time()
# df = get_telemetry_data_by_id(64689114)
# end_time = time.time()
# execution_time = end_time - start_time
# print(f'Duration: {execution_time}')
# print(df.info())
# print(df)


# start_time = time.time()
# df = get_telemetry_data_by_id_date_range(64689114, '2023-06-30 16:18:11.6482','2023-06-30 16:21:08.4202')
# end_time = time.time()
# execution_time = end_time - start_time
# print(f'Duration: {execution_time}')
# print(df.info())
# print(df)