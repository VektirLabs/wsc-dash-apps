import pandas as pd
import streamlit as st
import numpy as np
import warnings
import plotly.graph_objects as go
warnings.simplefilter(action='ignore', category=FutureWarning)
from scipy.interpolate import CubicSpline
from datetime import datetime
import pickle
import plotly_express as px
import base64
from io import BytesIO
from streamlit_option_menu import option_menu

# App config --------------------------------------------------------
st.set_page_config(
    page_title="Freeze Protect App",
    page_icon="temperature",
    layout="wide",
    # initial_sidebar_state="collapsed"
)
# Sidebar section ---------------------------------------------------
sb = st.sidebar

# Header section ----------------------------------------------------
c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header(":snowflake: WSC - Freeze Protect App")
with c2:
    st.image('static/conoco_logo.png', width=225)

# Tabs | Columns | Containers ---------------------------------------
tab_setup, tab_analysis = st.tabs(['Setup', 'Analysis'])
c11, c12, c13 = st.columns([0.25,0.30,0.45])

# Classes | Functions ------------------------------------------------
def initial_setup():
    """
    Create output of initial setup objects to capture the users input
    :return:DF of required input
    """
    list_well_info = ['Surface Casing Shoe MD (ft\')',
                     'Surface Casing Shoe TVD (ft\')',
                     'Surface Casing Shoe FIT/LOT weight (ppg)',
                     'Freeze Protect Depth (md)',
                     'Surface Casing ID (in)',
                     'Intermediate Casing OD (in)',
                     'Mud Weight Behind INT Casing (ppg)',
                     'Freeze Protect Fluid Weight (ppg)']
    list_params2 = [0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00]

    df_input = pd.DataFrame(data=list_params2, columns=['Input'])
    df_input = df_input.set_index([pd.Index(list_well_info)])
    df_input['Input'] = pd.to_numeric(df_input['Input'])

    return df_input

def check_column_not_zero(df, column_name):
    """
    Check if all values in the specified column of the DataFrame are not equal to 0.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    column_name (str): The name of the column to check.

    Returns:
    bool: True if all values in the column are not equal to 0, False otherwise.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    return df[column_name].ne(0).all()

def filter_columns(dataframe):
    """
        Filters the input dataframe by keeping only columns with names
                containing specified keywords.

        Parameters:
        dataframe (pd.DataFrame): The input dataframe to filter.

        Returns:
        pd.DataFrame: A new dataframe containing only the filtered columns.
                If no columns match the keywords, an empty dataframe is returned.
        """

    keywords = ['depth', 'md', 'measured depth',
                'inclination', 'inc',
                'az', 'azi', 'azm','azimuth',
                'total vertical depth', 'tvd',
                'vertical section', 'vs']

    # Create an empty dataframe for storing the filtered columns
    filtered_dataframe = pd.DataFrame()

    # Loop through the column names and check for the presence of any keyword
    for column_name in dataframe.columns:
        for keyword in keywords:
            if keyword.lower() in column_name.lower():
                filtered_dataframe[column_name] = dataframe[column_name]
                break

    filt_df = pd.DataFrame(filtered_dataframe)
    filt_df.columns = ['Md', 'Inc', 'Azm', 'Tvd', 'Vs']
    filt_df = filt_df.sort_values(by='Md',ascending=True)
    filt_df = filt_df.reset_index(drop=True).copy()
    return filt_df

def resample_survey_to_one_foot_intervals_cubic_df(survey_df):
    """
    Resamples the input survey dataframe to one-foot intervals using cubic interpolation.

    Parameters:
    survey_df (pd.DataFrame): The input survey dataframe with columns for "md", "inc", "az", and "tvd".

    Returns:
    List[np.ndarray]: A list of resampled station arrays, each containing depth, inclination, azimuth, and TVD.
    """
    # Initialize an empty df to store the resampled stations
    resampled_df = pd.DataFrame()
    svy_df = pd.DataFrame()

    try:
        svy_df = filter_columns(survey_df)
    except:
        st.write('Could not find the correct column names for reference. Need {"md", "inc", "az", "tvd"}')

    # Loop through each pair of consecutive stations in the filtered survey dataframe
    for i in range(len(svy_df) - 1):
        # Get the current station and the next station
        station1 = svy_df.iloc[i]
        station2 = svy_df.iloc[i + 1]

        # Extract depth, inclination, azimuth, and TVD for each station
        depth1, inclination1, azimuth1, tvd1, vs1 = station1
        depth2, inclination2, azimuth2, tvd2, vs2 = station2

        # Calculate the number of intervals between the two depths (rounded to the nearest integer)
        intervals = int(depth2 - depth1)

        # Create an array of depths at one-foot intervals between the two stations
        depths = np.linspace(depth1, depth2, intervals + 1)

        # Perform cubic interpolation for inclination, azimuth, and TVD between the two stations
        inclinations_spline = CubicSpline([depth1, depth2], [inclination1, inclination2])
        azimuths_spline = CubicSpline([depth1, depth2], [azimuth1, azimuth2])
        tvds_spline = CubicSpline([depth1, depth2], [tvd1, tvd2])
        vss_spline = CubicSpline([depth1, depth2], [vs1, vs2])

        # Evaluate the interpolated values at the resampled depths
        inclinations = inclinations_spline(depths)
        azimuths = azimuths_spline(depths)
        tvds = tvds_spline(depths)
        vss = vss_spline(depths)

        # Combine the resampled depths, inclinations, azimuths, TVDs, VSs into a single array
        stations = np.column_stack((depths, inclinations, azimuths, tvds, vss))

        # Append the resampled stations to the dataframe, excluding the last station to avoid duplicates
        resampled_df = resampled_df.append(pd.DataFrame(stations[:-1], columns=['md', 'inc', 'az', 'tvd', 'vs']),
                                           ignore_index=True)
    return resampled_df

def save_pkl(df1, df2, df3):
    with BytesIO() as buffer:
        pickle.dump((df1, df2, df3), buffer)
        buffer.seek(0)
        return buffer.getvalue()

def load_pkl(file):
    with file:
        return pickle.load(file)

@st.cache_resource
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Globals Variables -------------------------------------------------
# todo: set as sesions state varibles
WELL_NAME = ""
# WELL_NAME_SERIES = pd.Series()
WELL_INFO = pd.DataFrame()
DF_INPUT = pd.DataFrame()
SURVEY_DATA = pd.DataFrame()
DF_PUMP_SCHEDULE = pd.DataFrame()
SURVEYS_UPLOADED = False
MUD_GRADIENT = 0.052
BBL_CONV = 1029.4
PRE_FLUSH_CHECK = False
PRE_FLUSH_VOLUME = 0
PRE_FLUSH_WEIGHT = 8.34
SUCCESS_CHECK_RESULT_C11 = False
SUCCESS_CHECK_RESULT_C12 = False
SUCCESS_CHECK_RESULT_C13 = False
DT_NOW = datetime.today().strftime('%m-%d-%Y %H:%M:%S')
TEMP_PKL_PATH = 'static/FPA_Template Well_03212023194052.pkl'
PICKLE_FILE = None
SUCCESS_TEMP_OR_TEMP_PKL = False
SUCCESS_TEMP = False

with sb:
    # Use Template well pickle file
    rdo_template = sb.radio('Use Template Well?',('No','Yes'), horizontal=True)
    if rdo_template == 'Yes':
        with open(TEMP_PKL_PATH, 'rb') as f:
            WELL_INFO, DF_INPUT, SURVEY_DATA = pickle.load(f)
        SUCCESS_TEMP_OR_TEMP_PKL = True
        SUCCESS_TEMP = True
        sb.success('Success - Template well loaded!', icon="✅")
    sb.markdown("---")

    # Upload previously saved pickle file
    PICKLE_FILE = st.file_uploader("Upload Previous FPA well", type=["pkl"])
    sb.caption('Note: Previously saved files will have a .pkl extension')

    # Load and display the DataFrames from the uploaded .pkl file
    if PICKLE_FILE is not None:
        df1, df2, df3 = load_pkl(PICKLE_FILE)
        WELL_INFO = df1
        DF_INPUT = df2
        SURVEY_DATA = df3
        SUCCESS_TEMP_OR_TEMP_PKL = True
        SUCCESS_TEMP = False
        sb.success('Success - Previous FPA loaded!', icon="✅")

with tab_setup:
    c11, c12, c13 = st.columns([0.33, 0.33, 0.33])

    if not SUCCESS_TEMP_OR_TEMP_PKL:
        # Load Initial well name and info from Pickle file
        with c11:
            c11.markdown('### Step 1') # ------------------------------------
            c11.markdown('- Add well name and required input data below')
            c11.markdown('---')

            success_check_c11 = c11.empty()

            WELL_NAME = c11.text_input('Well Name')

            is_preflush = c11.radio('Include Pre-flush?', ('No', 'Yes'),horizontal=True)
            if is_preflush == 'Yes':
                PRE_FLUSH_VOLUME = c11.number_input('How many Barrels?')
                PRE_FLUSH_WEIGHT = c11.slider('Fluid weight', 6.8, 22.0, value=8.34, step=0.1)
            else:
                PRE_FLUSH_VOLUME = 0

            PRE_FLUSH_CHECK = True if is_preflush == 'Yes' else False

            DF_INPUT = c11.experimental_data_editor(initial_setup(), use_container_width=True)

            WELL_INFO = pd.Series({
                        'Well_Name': WELL_NAME,
                        'Date Time': DT_NOW,
                        'is_pre_flush': PRE_FLUSH_CHECK,
                        'pre_flush_vol': PRE_FLUSH_VOLUME,
                        'pre_flush_wt': PRE_FLUSH_WEIGHT
                        })

            SUCCESS_CHECK_RESULT_C11 = check_column_not_zero(DF_INPUT, 'Input')
            if SUCCESS_CHECK_RESULT_C11 and len(WELL_NAME) > 0:
                success_check_c11.success(' All well input fields are updated!', icon="✅")

        # upload survey info
        with c12:
            c12.markdown('### Step 2') # ------------------------------------
            c12.markdown(" - Upload your Survey Data (Md, Inc°, Azm°, Tvd, Vs)")
            c12.markdown("---")

            success_check_c12 = c12.empty()

            # Create file uploader and check files type
            uploaded_file = st.file_uploader("Choose file type ('.xlsx' or '.csv')", type=['xlsx', 'csv'])

            # Get Survey data and resample to 1' intervals
            if uploaded_file is not None:
                try:
                    SURVEY_DATA = pd.read_excel(uploaded_file)
                except:
                    try:
                        SURVEY_DATA = pd.read_csv(uploaded_file)
                    except:
                        print("Error uploading Survey file")

                if SURVEY_DATA.columns is not None:
                    success_check_c12.success(' Survey file successfully uploaded!', icon="✅")
                    SURVEYS_UPLOADED = True
                    SUCCESS_CHECK_RESULT_C12 = True
                    SURVEY_DATA = resample_survey_to_one_foot_intervals_cubic_df(SURVEY_DATA)

        # Preview and QC data - Save
        with c13:
            c13.markdown('### Step 3')
            c13.markdown('- Review all data then proceed to the Analysis Tab')
            c13.markdown('---')

            success_check_c13 = c13.empty()
            success_save_pkl_c13 = c13.empty()

            if SUCCESS_CHECK_RESULT_C11:
                c13.markdown(f"**Preview** - Well Info")
                c13.json(WELL_INFO.to_json(), expanded=False)
                c13.markdown('**Preview** - Well Input Parameters')
                c13.json(DF_INPUT.to_json(),expanded=False)

            if SUCCESS_CHECK_RESULT_C12:
                c13.markdown('**Preview** - Input Survey Data')
                c13.caption('Note: Survey file has been cleaned and interpolated')
                c13.dataframe(SURVEY_DATA, use_container_width=True)

            if SUCCESS_CHECK_RESULT_C11 and SUCCESS_CHECK_RESULT_C12:
                SUCCESS_CHECK_RESULT_C13 = True
                success_check_c13.success(' All input data is updated! --> Proceed to Analysis Tab', icon="✅")

                file_name = f"FPA_{WELL_NAME}_{datetime.today().strftime('%m%d%Y%H%M%S')}.pkl"

                # Button to download the DataFrames
                btn_save_pkl = success_save_pkl_c13.download_button(
                    label='Save Project',
                    data=save_pkl(WELL_INFO, DF_INPUT, SURVEY_DATA),
                    file_name=file_name,
                    mime='application/octet-stream'
                )

    else: # load from pickle file or template pickle file
        # Load Initial well name and info from Pickle file
        with c11:
            c11.markdown('### Step 1')  # ------------------------------------
            c11.markdown('- Add well name and required input data below')
            c11.markdown('---')

            success_check_c11 = c11.empty()

            WELL_NAME = c11.text_input('Well Name', value=WELL_INFO.iloc[0])

            is_preflush = WELL_INFO.iloc[2]
            if is_preflush == True:
                is_preflush = c11.radio('Include Pre-flush?',('No','Yes'),horizontal=True, index=1)
            else:
                is_preflush = c11.radio('Include Pre-flush?', ('No', 'Yes'), horizontal=True, index=0)

            if is_preflush == 'Yes':
                PRE_FLUSH_VOLUME = c11.number_input('How many Barrels?', value=WELL_INFO.iloc[3])
                PRE_FLUSH_WEIGHT = c11.slider('Fluid weight', 6.8, 22.0, value=WELL_INFO.iloc[4], step=0.1)
            else:
                PRE_FLUSH_VOLUME = 0

            PRE_FLUSH_CHECK = True if is_preflush == 'Yes' else False

            DF_INPUT = c11.experimental_data_editor(DF_INPUT, use_container_width=True)

            WELL_INFO = pd.Series({
                'Well_Name': WELL_NAME,
                'Date Time': DT_NOW,
                'is_pre_flush': PRE_FLUSH_CHECK,
                'pre_flush_vol': PRE_FLUSH_VOLUME,
                'pre_flush_wt': PRE_FLUSH_WEIGHT
            })
            # SUCCESS_CHECK_RESULT_C11 = check_column_not_zero(DF_INPUT, 'Input')
            SUCCESS_CHECK_RESULT_C11 = True
            if SUCCESS_CHECK_RESULT_C11 and len(WELL_NAME) > 0:
                success_check_c11.success(' All well input fields are updated!', icon="✅")

        # Load survey info Pickle file
        with c12:
           if SUCCESS_TEMP: # if loading temp file do not load surveys
                c12.markdown('### Step 2')  # ------------------------------------
                c12.markdown(" - Upload your Survey Data (Md, Inc°, Azm°, Tvd, Vs)")
                c12.markdown("---")

                success_check_c12 = c12.empty()

                # Create file uploader and check files type
                uploaded_file = st.file_uploader("Choose file type ('.xlsx' or '.csv')", type=['xlsx', 'csv'])

                # Get Survey data and resample to 1' intervals
                if uploaded_file is not None:
                    try:
                        SURVEY_DATA = pd.read_excel(uploaded_file)
                    except:
                        try:
                            SURVEY_DATA = pd.read_csv(uploaded_file)
                        except:
                            print("Error uploading Survey file")

                    if SURVEY_DATA.columns is not None:
                        success_check_c12.success(' Survey file successfully uploaded!', icon="✅")
                        SURVEYS_UPLOADED = True
                        SUCCESS_CHECK_RESULT_C12 = True
                        SURVEY_DATA = resample_survey_to_one_foot_intervals_cubic_df(SURVEY_DATA)
           else:
                c12.markdown('### Step 2')  # ------------------------------------
                c12.markdown(" - Upload your Survey Data (Md, Inc°, Azm°, Tvd, Vs)")
                c12.markdown("---")

                success_check_c12 = c12.empty()

                if SURVEY_DATA.columns is not None:
                    success_check_c12.success(' Survey file successfully uploaded!', icon="✅")
                    SURVEYS_UPLOADED = True
                    SUCCESS_CHECK_RESULT_C12 = True
                    SURVEY_DATA = SURVEY_DATA
                c12.markdown(f'##### Survey Preview')
                c12.dataframe(SURVEY_DATA.head(10), use_container_width=True)

        # Preview and QC data - Save as new
        with c13:
            c13.markdown('### Step 3')
            c13.markdown('- Review all data then proceed to the Analysis Tab')
            c13.markdown('---')

            success_check_c13 = c13.empty()
            success_save_pkl_c13 = c13.empty()

            if SUCCESS_CHECK_RESULT_C11:
                c13.markdown(f"**Preview** - Well Info")
                c13.json(WELL_INFO.to_json(),expanded=False)
                c13.markdown('**Preview** - Well Input Parameters')
                c13.json(DF_INPUT.to_json(),expanded=False)

            if SUCCESS_CHECK_RESULT_C12:
                c13.markdown('**Preview** - Input Survey Data')
                c13.caption('Note: Survey file has been cleaned and interpolated')
                c13.dataframe(SURVEY_DATA, use_container_width=True)

            if SUCCESS_CHECK_RESULT_C11 and SUCCESS_CHECK_RESULT_C12:
                SUCCESS_CHECK_RESULT_C13 = True
                success_check_c13.success(' All input data is updated! --> Proceed to Analysis Tab', icon="✅")

                file_name = f"FPA_{WELL_NAME}_{datetime.today().strftime('%m%d%Y%H%M%S')}.pkl"

                # Button to download the DataFrames
                btn_save_pkl = success_save_pkl_c13.download_button(
                    label='Save Project as new',
                    data=save_pkl(WELL_INFO, DF_INPUT, SURVEY_DATA),
                    file_name=file_name,
                    mime='application/octet-stream'
                )

with tab_analysis:
    c21, c22 = st.columns([0.33, 0.66])

    # Text output values
    with c21:
        c21.markdown('### Freeze Protect Overview')  # ------------------------------------
        num_emw = DF_INPUT.loc['Surface Casing Shoe FIT/LOT weight (ppg)'][0]
        num_test_psi = int(np.multiply(
                        np.multiply(num_emw,(DF_INPUT.loc["""Surface Casing Shoe TVD (ft')"""][0])), MUD_GRADIENT))
        num_surf_int_csg_capacity = round(np.divide(np.square(DF_INPUT.loc["""Surface Casing ID (in)"""][0]) -
                                      np.square(DF_INPUT.loc["""Intermediate Casing OD (in)"""][0]), BBL_CONV),4)
        num_annulus_vol_to_shoe = round(np.multiply(DF_INPUT.loc["""Surface Casing Shoe MD (ft')"""][0],
                                                    num_surf_int_csg_capacity),2)
        num_freeze_protect_vol = int(np.multiply(DF_INPUT.loc["""Freeze Protect Depth (md)"""][0],
                                                 num_surf_int_csg_capacity))
        txt_preflush = ""
        if PRE_FLUSH_CHECK:
            txt_preflush = f"""Pumping pre-flush water: **{PRE_FLUSH_CHECK}**, Volume: **{PRE_FLUSH_VOLUME} bbls**"""
        else:
            txt_preflush = f"""Pumping pre-flush water: **{PRE_FLUSH_CHECK}**"""

        txt_details = f"""
        - Well Name: **{WELL_NAME}**
        - Updated date: **{DT_NOW}**
        - Survey's have been upload: **{SURVEYS_UPLOADED}**
        - Perform annular LOT to Max pressure of: **{num_emw} ppg**
        - {txt_preflush}   

        #### Calculated Outpts
        - FIT | LOT pressure: **{num_test_psi} psi**
        - Surface by Int Casing Capacity: **{num_surf_int_csg_capacity} bbl/ft**
        - Annulus volume to Surface Shoe: **{num_annulus_vol_to_shoe} bbls**
        - Freeze Protect Volume: **{num_freeze_protect_vol} bbls**
        """
        c21.markdown(f'{txt_details}')

    srvy_data = SURVEY_DATA.copy()
    if srvy_data is not None:
        srvy_data['Fluid Btm MD'] = np.round(srvy_data['md'])
        # srvy_data

        # Create H20 fluid
        h20_fluid = pd.Series(np.arange(0, PRE_FLUSH_VOLUME, 1) + 1)
        h20_fluid_name = pd.Series(np.full(len(h20_fluid),'H20'))
        h20_fluid_wt = pd.Series(np.full(len(h20_fluid), WELL_INFO.iloc[4]))
        df_h20 = pd.concat([h20_fluid, h20_fluid_name, h20_fluid_wt], axis=1, sort=False, ignore_index=True)
        df_h20.columns = ['Fluid bbls','Fluid Type', 'Fluid Weight (ppg)']
        # df_h20

        # Create H20 fluid
        diesel_fluid = pd.Series(np.arange(0, num_freeze_protect_vol, 1) + 1)
        diesel_fluid = pd.Series(np.full(len(diesel_fluid), 'Diesel'))
        diesel_fluid = pd.Series(np.full(len(diesel_fluid), DF_INPUT.iloc[7]))
        df_diesel = pd.concat([diesel_fluid, diesel_fluid,diesel_fluid], axis=1, ignore_index=True)
        df_diesel.columns = ['Fluid bbls', 'Fluid Type','Fluid Weight (ppg)']

        # Combine fluid df into pump schedule df
        df_fluid = pd.concat([df_h20, df_diesel],axis=0, sort=False, ignore_index=True)
        df_fluid['Cuml bbl'] = pd.Series(np.arange(0,len(df_fluid),1)) +1
        df_pump_schedule = df_fluid[['Fluid Type', 'Fluid bbls', 'Fluid Weight (ppg)','Cuml bbl']]

            # Build pump schedule df
        df_pump_schedule['Fluid Top MD'] = np.zeros(len(df_pump_schedule))
        df_pump_schedule['Fluid Btm MD'] = round(np.divide(df_fluid['Cuml bbl'], num_surf_int_csg_capacity),0)

        df_ps_temp = df_pump_schedule.merge(srvy_data[['Fluid Btm MD','tvd']],on='Fluid Btm MD', how="left")
        df_pump_schedule['Fluid Btm Tvd'] = df_ps_temp.loc[:,'tvd']
        df_pump_schedule['Fluid Hydrostatic Psi'] = np.round(np.multiply(df_pump_schedule['Fluid Btm Tvd'],
                                                            df_pump_schedule['Fluid Weight (ppg)']) * MUD_GRADIENT)
        df_pump_schedule['Mud Top MD'] = df_pump_schedule['Fluid Top MD']
        df_pump_schedule['Mud Btm MD'] = pd.Series(np.full(len(df_pump_schedule), fill_value=DF_INPUT.iloc[0]))
        df_pump_schedule['Shoe Tvd'] = pd.Series(np.full(len(df_pump_schedule), fill_value=DF_INPUT.iloc[1]))
        df_pump_schedule['Mud bbls in Hole'] = df_pump_schedule['Cuml bbl'] * num_surf_int_csg_capacity
        df_pump_schedule['Mud Btm Tvd'] = np.round(np.subtract(df_pump_schedule['Shoe Tvd'],
                                                               df_pump_schedule['Fluid Btm Tvd']))
        df_pump_schedule['Mud Hydrostatic Psi'] =np.round(
                        np.multiply(df_pump_schedule['Mud Btm Tvd'],
                        pd.Series(np.full(len(df_pump_schedule),fill_value=DF_INPUT.iloc[6]))) * MUD_GRADIENT)
        df_pump_schedule['MASP'] = np.subtract(pd.Series(np.full(len(df_pump_schedule),fill_value=num_test_psi)),
                                 np.add(df_pump_schedule['Fluid Hydrostatic Psi'],df_pump_schedule['Mud Hydrostatic Psi']))
        # display cols [[]]
        DF_PUMP_SCHEDULE = df_pump_schedule

    # Graph visuals
    with c22:
        if DF_PUMP_SCHEDULE is not None:
            st.subheader("Pump Down Schedule and Graph")
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=DF_PUMP_SCHEDULE['Cuml bbl'],
                y=DF_PUMP_SCHEDULE['MASP'],
                mode='lines',
                name='Type A',
                fill='tozeroy',
                line=dict(width=2, color='blue')
            ))

            # Customize the layout of the plot
            fig.update_layout(
                # title='Pump Down Schedule and Graph',
                xaxis_title='Cumulative Bbls Pumped',
                yaxis_title='Pressure delta',
                showlegend=True
            )

            c22.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([0.9, 0.1])

        col1.markdown("#### Detailed - Pump Schedule")
        cols = ['Fluid Type', 'Fluid bbls', 'Fluid Weight (ppg)', 'Cuml bbl', 'Fluid Btm MD', 'Fluid Btm Tvd',
                'Fluid Hydrostatic Psi',  'Mud Btm MD', 'Shoe Tvd', 'Mud bbls in Hole', 'Mud Btm Tvd', 'Mud Hydrostatic Psi', 'MASP']
        csv = convert_df(DF_PUMP_SCHEDULE)
        col2.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='Pump Schedule.csv',
            mime='text/csv',
        )
        st.dataframe(DF_PUMP_SCHEDULE, use_container_width=True)
