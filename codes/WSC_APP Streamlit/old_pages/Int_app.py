import streamlit as st
from streamlit_modal import Modal
import streamlit.components.v1 as components
import pandas as pd
pd.options.display.float_format = '{:.4f}'.format
import numpy as np
import pickle
import io
from io import BytesIO
from scipy.interpolate import CubicSpline
import welleng as we
import warnings
import plotly.graph_objects as go
warnings.simplefilter(action='ignore', category=FutureWarning)
# https://github.com/engrinak/Well-Path-Simulator/blob/master/WellPathSimulator.py

# App config --------------------------------------------------------
st.set_page_config(
    page_title="Interpolator 1 Apps",
    page_icon="earth_america",
    layout="wide",
    # initial_sidebar_state="collapsed"
)
# Globals -----------------------------------------------------------
DF_IN = pd.DataFrame({
    "Measured Depth": [0],
    "Inclination": [0],
    "Azimuth": [0],
})

# Session state variables -------------------------------------------
if "df_in" not in st.session_state:
    st.session_state['df_in'] = DF_IN

if "srvy_data_in" not in st.session_state:
    st.session_state['srvy_data_in'] = DF_IN

# Retrieve the info
# DF_IN = st.session_state['df_in']
SURVEY_DATA_IN = st.session_state['srvy_data_in']

# Set DF_IN Types
DF_IN['Measured Depth'] = DF_IN['Measured Depth'].astype('float')
DF_IN['Inclination'] = DF_IN['Inclination'].astype('float')
DF_IN['Azimuth'] = DF_IN['Azimuth'].astype('float')

# Classes | Functions -----------------------------------------------
def calc_min_curve(df_in):
    df = df_in.copy()

    df['Md'] = df['Measured Depth']
    df['CL'] = np.subtract(df['Measured Depth'], df['Measured Depth'].shift(1))
    # df['CL'][0] = df["Md"][0]
    df['Inc'] = df['Inclination']
    df['Azm'] = df['Azimuth']

    df['Inc 1'] = np.radians(df['Inclination'])
    df['Inc 2'] = np.radians(df['Inclination'].shift(1))
    df['Inc 1'][0] = df["Inc"][0]
    df['Azm 1'] = np.radians(df['Azimuth'])
    df['Azm 2'] = np.radians(df['Azimuth'].shift(1))

    df['Dls'] = np.divide(np.degrees(np.arccos(np.cos(df['Inc 2'] - df['Inc 1']) - (np.sin(df['Inc 1'])*np.sin(df['Inc 2'])*(1-np.cos(df['Azm 2']-df['Azm 1']))))),df["CL"]) * 100
    df["Beta"] = df["Dls"].apply(lambda DLS: 1 if DLS == 0 else (2/DLS) * np.tan(np.radians(DLS/2)))
    df['NS'] = (df['CL'] / 2) * (np.sin( df['Inc 1']) * np.cos(df['Azm 1']) + np.sin( df['Inc 2']) * np.cos(df['Azm 2'])) * df["Beta"]
    df["EW"] = (df['CL'] / 2) * (np.sin(df['Inc 1']) * np.sin(df['Azm 1']) + np.sin(df['Inc 2']) * np.sin(df['Azm 2'])) * df["Beta"]
    df["TVD"] = df.apply(lambda row: row["CL"] if row["Inc 1"] == row["Inc 2"] == 0 else (row["CL"] / 2) * (np.cos(np.radians(row["Inc 1"])) + np.cos(np.radians(row["Inc 2"]))) * row["Beta"], axis=1)

    return df

def calulate_survey(df):
    df.columns = ['MD', 'INC', 'AZI']
    df['MD'] = df['MD']
    df['INC'] = df['INC']
    df['AZI'] = df['AZI']
    df['I1'] = df['INC'].shift(1)
    df['A1'] = df['AZI'].shift(1)
    df['CL'] = df['MD'] - df['MD'].shift(1)

    # If not starting from zero:
    #       Set the CL to the first MD
    #       Set the previous Inc to the current Inc
    df['CL'][0] = df['MD'][0]
    df['I1'][0] = df['INC'][0]

    res_df = df.apply(
        lambda x: min_curve_calc(
            x['CL'],
             x['I1'],
             x['INC'],
             x['A1'],
             x['AZI']),
            axis=1,
            result_type='expand')

    res_df.columns = ['NS', 'EW', 'TVD', 'DLS', 'RF']
    # resdf['TVD'] = -resdf['TVD']

    df_final = pd.concat([df, res_df], axis=1)

    df_final['NS'] = df_final['NS'].cumsum()
    df_final['EW'] = df_final['EW'].cumsum()
    df_final['TVD'] = df_final['TVD'].cumsum()
    df_final['DLS'] = (np.divide(np.degrees(df_final['DLS']), df_final['CL']) ) * 100
    return df_final

def min_curve_calc(MD, I1, I2, A1, A2):
    I1 = np.radians(I1)
    I2 = np.radians(I2)
    A1 = np.radians(A1)
    A2 = np.radians(A2)
    DLS = np.arccos(np.cos(I2 - I1) - (np.sin(I1)*np.sin(I2)*(1-np.cos(A2-A1))))

    # If they put in a straight line survey or if
    # there is a survey station with exactly the
    # same inc and azi as the previous station
    # This avoids divide by zero problems
    if DLS == 0:
        RF = 1
    else:
        RF = (2/DLS) * np.tan(DLS/2)

    NS = (MD / 2) * (np.sin(I1) * np.cos(A1) + np.sin(I2) * np.cos(A2)) * RF
    EW = (MD / 2) * (np.sin(I1) * np.sin(A1) + np.sin(I2) * np.sin(A2)) * RF

    # When starting from zero inclination, TVD == MD
    if I1 == I2 == 0:
        TVD = MD
    else:
        TVD = (MD / 2) * (np.cos(I1) + np.cos(I2)) * RF


    return NS, EW, TVD, DLS, RF

def download_surveys(name,df):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_str = csv_buffer.getvalue()

    # Add a download button to download the CSV
    st.download_button(
        label="Download Interpolated Survey File",
        data=csv_str,
        file_name=f"{name}_Interpolated_Surveys.csv",
        mime="text/csv"
    )

def save_pkl(df1, df2, df3):
    with BytesIO() as buffer:
        pickle.dump((df1, df2, df3), buffer)
        buffer.seek(0)
        return buffer.getvalue()

def load_pkl(file):
    with file:
        return pickle.load(file)


# Create sidebar ----------------------------------------------------
sb = st.sidebar

# Create header sections --------------------------------------------
c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header(":earth_americas: WSC - Interpolator App")
    st.markdown('''To use this app simply upload your survey data and use the 
    input fields to filter/adjust the interpolated data''')
with c2:
    st.image('static/conoco_logo.png', width=225)
st.divider()

# Create components -------------------------------------------------
cnt_md = st.container()
cnt_tvd = st.container()

c11, c12, c13 = st.columns([0.30, 0.30, 0.40],gap='large')

# Step 1 - Copy/Paste surveys
with c11:
    st.markdown("#### Step 1")
    st.caption('Copy and paste your survey data below [MD, Inc, Azm]')

    df_out = st.experimental_data_editor(DF_IN, use_container_width=True, num_rows='dynamic')
    btn_submit = st.button('Submit', use_container_width=True)

    if btn_submit:
        st.session_state['srvy_data_in'] = df_out
        st.success('Success, Surveys Submitted!')

# Step 2 - Adjust filtering/fields
with c12:
    st.markdown("#### Step 2")
    st.caption('Make the proper selections below:')

    # Swap MD <--> TVD Components based on radio control
    rdo_interpolate_by = c12.radio('**Interpolate by:**',
                                ('Measured Depth', 'True Vertical Depth'),
                                horizontal=True,
                                key='rdo_interpolate_by'
                                )
    if rdo_interpolate_by == 'Measured Depth':
        with cnt_md:
            if SURVEY_DATA_IN is not None:
                rdo_md_swap = c12.radio('Filter by:', ('Single', 'Range'), horizontal=True, key='rdo_md_swap')
                if rdo_md_swap == 'Single':
                    SLD_MD_SINGLE = c12.number_input('Single - Measured Depth (Md)',
                                                     key='single_md_input')
                    st.session_state["single_md_value"] = SLD_MD_SINGLE
                    c12.write('Filtered results by value')
                else:
                    c111, c112 = c12.columns([0.5, 0.5])
                    SLD_MD_MIN = c111.number_input('Min - Measured Depth (Md)',
                                                   key='min_md_input')
                    st.session_state["min_md_value"] = SLD_MD_MIN

                    SLD_MD_MAX = c112.number_input('Max - Measured Depth (Md)',
                                                   key='max_md_input')
                    st.session_state["max_md_value"] = SLD_MD_MAX
                    c12.write('Filtered results by range')
            else:
                output_md_data = c12.empty()
    else:
        with cnt_tvd:
            if SURVEY_DATA_IN is not None:
                rdo_tvd_swap = c12.radio('Filter by:', ('Single', 'Range'), horizontal=True, key='rdo_tvd_swap')
                if rdo_tvd_swap == 'Single':
                    SLD_TVD_SINGLE = c12.number_input('Single - True Vertical Depth (Tvd)',
                                                      key='single_tvd_input')
                    st.session_state["single_tvd_value"] = SLD_TVD_SINGLE
                    c11.write('Filtered results by value')
                else:
                    c121, c122 = c12.columns([0.5, 0.5])
                    SLD_TVD_MIN = c121.number_input('Min -  True Vertical Depth (Tvd)',
                                                    key='min_tvd_input')
                    st.session_state["min_tvd_value"] = SLD_TVD_MIN

                    SLD_TVD_MAX = c122.number_input('Max -  True Vertical Depth (Tvd)',
                                                    key='max_tvd_input')
                    st.session_state["max_tvd_value"] = SLD_TVD_MAX
                    c12.write('Filtered results by range')
            else:
                output_md_data = c12.empty()

# Step 3 - Preview data
with c13:
    st.markdown("#### Preview Output Data")
    with st.expander('Original Data'):
        st.table(st.session_state['srvy_data_in'])

    with st.container():
        layout = go.Layout(
            title="Original vs. Interpolated Surveys",
            height=550,
            xaxis=dict(title="VS"),
            yaxis=dict(title="TVD")
        )
        fig = go.Figure(layout=layout)
        c13.plotly_chart(fig, use_container_width=True)

    with st.expander('Interpolated Data'):
        st.table(SURVEY_DATA_IN)


# def interpolate_surveys(DF_IN):

DF = df_out.copy()
DF["Md"] = DF['Measured Depth']
DF["CL"] = DF['Measured Depth'] - DF['Measured Depth'].shift(1)
DF["Inc"] = DF['Inclination']
DF["Inc2"] = DF['Inclination'].shift(1)
DF["Azi"] = DF['Azimuth']
DF["Azi2"] = DF['Azimuth'].shift(1)
DF['CL'][0] = DF['Md'][0]
DF['Inc'][0] = DF['Inc2'][0]
DF = DF.fillna(0)

I1 = np.radians(DF["Inc"])
I2 = np.radians(DF["Inc2"])
A1 = np.radians(DF["Azi"])
A2 = np.radians(DF["Azi2"])
DLS = np.arccos(np.cos(I2 - I1) - (np.sin(I1) * np.sin(I2) * (1 - np.cos(A2 - A1))))
CL = DF['Md'] - DF['Md'].shift(1)

if any(DLS) == 0:
    RF = 1
else:
    RF = (2 / DLS) * np.tan(DLS / 2)

NS = (CL / 2) * (np.sin(I1) * np.cos(A1) + np.sin(I2) * np.cos(A2)) * RF
EW = (CL / 2) * (np.sin(I1) * np.sin(A1) + np.sin(I2) * np.sin(A2)) * RF

# When starting from zero inclination, TVD == MD
if any(I1) == any(I2) == 0:
    TVD = CL
else:
    TVD = (CL / 2) * (np.cos(I1) + np.cos(I2)) * RF

DF["Md"] = DF['Measured Depth']
DF['Tvd'] = TVD
DF["Inc"] = DF['Inclination']
DF["Azi"] = DF['Azimuth']
DF['CL'] = CL
DF['Dls'] = DLS
DF['Ns'] = NS
DF['Ew'] = EW
DF['RF'] = RF
DF = DF.fillna(0)
#
# # df_list = [MD, I1, A1, NS, EW, TVD, DLS, CL, RF ]
# # df_cols = ["Md", "Inc", "Azi", "Ns", "Ew", "Tvd", "DLS", "CL", "RF"]
# df_final = DF #  pd.concat(df_list, axis=1, names=df_cols)
#
DF['Ns'] = DF['Ns'].cumsum()
DF['Ew'] = DF['Ew'].cumsum()
DF['Tvd'] = DF['Tvd'].cumsum()
DF['Dls'] = (np.divide(np.degrees(DF['Dls']) , DF['CL'])) * 100

    # return DF

# st.table(interpolate_surveys(DF_IN))
st.write(DF)