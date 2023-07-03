import streamlit as st
import pandas as pd
import numpy as np
import pickle
import io
from io import BytesIO
from scipy.interpolate import CubicSpline
import warnings
import plotly.graph_objects as go
warnings.simplefilter(action='ignore', category=FutureWarning)

# App config ----------------------------------------------------
st.set_page_config(
    page_title="Interpolator 1 Apps",
    page_icon="earth_america",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# Classes | Functions -----------------------------------------------
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
                'vertical section', 'vs',
                'northings', 'north', 'ns', 'n',
                'eastings', 'east', 'ew','e'
                'dogleg','doglegs','dls'
                ]

    # Create an empty dataframe for storing the filtered columns
    filtered_dataframe = pd.DataFrame()

    # Loop through the column names and check for the presence of any keyword
    for column_name in dataframe.columns:
        for keyword in keywords:
            if keyword.lower() in column_name.lower():
                filtered_dataframe[column_name] = dataframe[column_name]
                break

    filt_df = pd.DataFrame(filtered_dataframe)
    filt_df.columns = ['Md', 'Inc', 'Azm', 'Tvd', 'Vs', 'Nth', 'Est', 'Dls']
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
        st.markdown(f'''**Parsing Error:** Could not find the correct column names! 
        - Columns needed ["md", "inc", "az", "tvd", "vs", "ns", "ew", "dls]''')

    # Loop through each pair of consecutive stations in the filtered survey dataframe
    for i in range(len(svy_df) - 1):
        # Get the current station and the next station
        station1 = svy_df.iloc[i]
        station2 = svy_df.iloc[i + 1]

        # Extract depth, inclination, azimuth, and TVD for each station
        depth1, inclination1, azimuth1, tvd1, vs1, ns1, ew1, dls1 = station1
        depth2, inclination2, azimuth2, tvd2, vs2, ns2, ew2, dls2 = station2

        # Calculate the number of intervals between the two depths (rounded to the nearest integer)
        intervals = int(depth2 - depth1)

        # Create an array of depths at one-foot intervals between the two stations
        depths = np.linspace(depth1, depth2, intervals + 1)

        # Perform cubic interpolation for inclination, azimuth, and TVD between the two stations
        inclinations_spline = CubicSpline([depth1, depth2], [inclination1, inclination2])
        azimuths_spline = CubicSpline([depth1, depth2], [azimuth1, azimuth2])
        tvds_spline = CubicSpline([depth1, depth2], [tvd1, tvd2])
        vss_spline = CubicSpline([depth1, depth2], [vs1, vs2])
        ns_spline = CubicSpline([depth1, depth2], [ns1, ns2])
        ew_spline = CubicSpline([depth1, depth2], [ew1, ew2])
        dls_spline = CubicSpline([depth1, depth2], [dls1, dls2])

        # Evaluate the interpolated values at the resampled depths
        inclinations = inclinations_spline(depths)
        azimuths = azimuths_spline(depths)
        tvds = tvds_spline(depths)
        vss = vss_spline(depths)
        ns = vss_spline(depths)
        ew = vss_spline(depths)
        dls = vss_spline(depths)

        # Combine the resampled depths, inclinations, azimuths, TVDs, VSs into a single array
        stations = np.column_stack((depths, inclinations, azimuths, tvds, vss,ns, ew, dls))

        # Append the resampled stations to the dataframe, excluding the last station to avoid duplicates
        resampled_df = resampled_df.append(pd.DataFrame(stations[:-1], columns=['Md', 'Inc', 'Az', 'Tvd', 'Vs', 'Ns', 'Ew', 'Dls']),
                                           ignore_index=True)
        resampled_df = resampled_df.ffill()
    return resampled_df

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

def plot_surveys(df1, df2):

    try:
        # todo: fix hover labels
        # hover_template = (
        #      "<b>Depth:</b> %{customdata[0]:.2f}<br>"
        #      "<b>TVD:</b> %{customdata[1]:.2f}<br>"
        #      "<b>Inc:</b> %{customdata[2]:.2f}<br>"
        #      "<b>Az:</b> %{customdata[3]:.2f}<br>"
        #      "<b>VS:</b> %{x:.2f}<br>"
        #      "<b>NS:</b> %{customdata[4]:.2f}<br>"
        #      "<b>EW:</b> %{customdata[5]:.2f}<br>"
        #      "<b>DLS:</b> %{customdata[6]:.2f}<extra></extra>"
        # )

        # Original surveys
        trace1 = go.Scatter(
            x=df1["VS"],
            y=df1["TVD"] * -1,
            mode="markers+lines",
            name="Original Surveys",
            line=dict(color="rgba(211, 211, 211, 0.8)", width=5),  # light grey color with 60% transparency
            marker=dict(color="rgba(211, 211, 211, 0.8)")
        )

        # Interpolated surveys
        trace2 = go.Scatter(
            x=df2["Vs"],
            y=df2["Tvd"] * -1,
            mode="markers",
            name="Interpolated Surveys",
            line=dict(color="blue"),
            marker=dict(color="blue", size=5),
        )

        # Combine traces and create the layout
        data = [trace1, trace2]
        layout = go.Layout(
            title="Original vs. Interpolated Surveys",
            height = 750,
            xaxis=dict(title="VS"),
            yaxis=dict(title="TVD")
        )

        # Create the figure
        fig = go.Figure(data=data, layout=layout)
        fig.update_layout(hovermode="x unified")
        fig.add_vline(0, line=dict(color="rgba(211, 211, 211, 0.5)", width=2))
        fig.add_hline(0, line=dict(color="rgba(211, 211, 211, 0.5)", width=2))

        return fig
    except:
        layout = go.Layout(
            title="Original vs. Interpolated Surveys",
            height=750,
            xaxis=dict(title="VS"),
            yaxis=dict(title="TVD")
        )
        return go.Figure(layout=layout)

# Globals -----------------------------------------------------------
SURVEY_DATA_ORIGINAL = pd.DataFrame()
SURVEY_DATA = pd.DataFrame()
SURVEYS_UPLOADED = False
SUCCESS_CHECK_RESULT_c11 = True
FILTERED_SRVY_MD_DF = pd.DataFrame()
FILTERED_SRVY_TVD_DF = pd.DataFrame()
DF_IN = pd.DataFrame(
     {"Measured Depth": [0],
      "Inclination": [0],
      "Azimuth": [0],
})


SLD_MD_SINGLE = 0
SLD_MD_MIN = 0
SLD_MD_MAX = 0
SLD_TVD_SINGLE = 0
SLD_TVD_MIN = 0
SLD_TVD_MAX = 0

# Md Session state - Set defaults
if "min_md_value" not in st.session_state:
    st.session_state['min_md_value'] = 0
if "max_md_value" not in st.session_state:
    st.session_state["max_md_value"] = 0
if "single_md_value" not in st.session_state:
    st.session_state["single_md_value"] = 0

# Md Session state
if 'min_md_value' not in st.session_state:
    st.session_state.min_md_value = SURVEY_DATA['md'].astype('int').min()
if 'max_md_value' not in st.session_state:
    st.session_state.max_md_value = SURVEY_DATA['md'].astype('int').max()
if 'single_md_value' not in st.session_state:
    st.session_state.min_md_value = SURVEY_DATA['md'].astype('int').min()

# Tvd Session state - Set defaults
if "min_tvd_value" not in st.session_state:
    st.session_state["min_tvd_value"] = 0
if "max_tvd_value" not in st.session_state:
    st.session_state["max_tvd_value"] = 0
if "single_tvd_value" not in st.session_state:
    st.session_state["single_tvd_value"] = 0

# Tvd Session state
if 'min_tvd_value' not in st.session_state:
    st.session_state.min_md_value = SURVEY_DATA['tvd'].astype('int').min()
if 'max_tvd_value' not in st.session_state:
    st.session_state.max_md_value = SURVEY_DATA['tvd'].astype('int').max()
if "single_tvd_value" not in st.session_state:
    st.session_state["single_tvd_value"] = SURVEY_DATA['tvd'].astype('int').max()

sb = st.sidebar

c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header(":earth_americas: WSC - Interpolator App")
    st.markdown('''To use this app simply upload your survey data and use the input fields to filter/adjust the
     interpolated data''')
with c2:
    st.image('static/conoco_logo.png', width=225)

with sb:
    sb.markdown(f'''Upload your survey data to Interpolate.''')
    sb.markdown(f'''Required ["md", "inc", "az", "tvd", "vs", "ns", "ew", "dls]''')

    err_msg = st.empty()
    err_msg = st.error('Please upload your survey file', icon="🔥")

    # Create file uploader and check files type
    uploaded_file = sb.file_uploader("Choose file type ('.xlsx' or '.csv')", type=['xlsx', 'csv'])

    # Get Survey data and resample to 1' intervals
    if uploaded_file is not None:
        err_msg.empty()
        try:
            SURVEY_DATA = pd.read_excel(uploaded_file)
            SURVEY_DATA_ORIGINAL = SURVEY_DATA.copy()
        except:
            try:
                SURVEY_DATA = pd.read_csv(uploaded_file)
                SURVEY_DATA_ORIGINAL = SURVEY_DATA.copy()
            except:
                st.error("Error uploading Survey csv file...")

        if SURVEY_DATA.columns is not None:
            try:
                SURVEYS_UPLOADED = True
                SURVEY_DATA = resample_survey_to_one_foot_intervals_cubic_df(SURVEY_DATA)
            except:
                st.error('Please ensure you Survey file has the proper columns')

    # Download Interpolated surveys
    st.markdown('---')

    if SURVEYS_UPLOADED:
        show_dwnld = st.radio('Show file download area?', ('No', 'Yes'), horizontal=True)
        if show_dwnld == 'Yes':
            file_name = st.text_input('File name')
            if len(file_name) > 1:
                download_surveys(file_name, SURVEY_DATA)

c11, c13 = st.columns([0.35, 0.65])
# c11.markdown("---")
rdo_interpolate_by = c11.radio('**Interpolate by:**',
                               ('Measured Depth', 'True Vertical Depth'),
                               horizontal=True,
                               key='rdo_interpolate_by'
                               )
data_container = st.container()
md_container = st.container()
tvd_container = st.container()

DF_IN = DF_IN.convert_dtypes(infer_objects=True)
df_in = st.experimental_data_editor(DF_IN, use_container_width=True, num_rows='dynamic')


with c13:
    # Create plot of df's
    if SURVEY_DATA is not None and SURVEYS_UPLOADED is not None:
        c13.plotly_chart(plot_surveys(SURVEY_DATA_ORIGINAL, SURVEY_DATA), use_container_width=True)

if rdo_interpolate_by == 'Measured Depth':
    with md_container:
        c11.markdown('#### Filter by Measured Depth (Md)')  # ------------------------------------
        c11.markdown("---")

        if SURVEYS_UPLOADED:
            rdo_md_swap = c11.radio('Filter by:', ('Single', 'Range'), horizontal=True, key='rdo_md_swap')
            if rdo_md_swap == 'Single':
                SLD_MD_SINGLE = c11.number_input('Single - Measured Depth (Md)',
                                                          value=st.session_state["single_md_value"],
                                                          key='single_md_input')
                st.session_state["single_md_value"] = SLD_MD_SINGLE
                c11.write('Filtered results by value')
            else:
                c111, c112 = c11.columns([0.5, 0.5])
                SLD_MD_MIN = c111.number_input('Min - Measured Depth (Md)',
                                               value=st.session_state["min_md_value"],
                                               key='min_md_input')
                st.session_state["min_md_value"] = SLD_MD_MIN

                SLD_MD_MAX = c112.number_input('Max - Measured Depth (Md)',
                                               value=st.session_state["max_md_value"],
                                               key='max_md_input')
                st.session_state["max_md_value"] = SLD_MD_MAX
                c11.write('Filtered results by range')
        else:
            output_md_data = c11.empty()
else:
    with tvd_container:
        c11.markdown('### Filter by True vertical depth (Tvd)')  # ------------------------------------
        c11.markdown("---")

        if SURVEYS_UPLOADED:
            rdo_tvd_swap = c11.radio('Filter by:', ('Single', 'Range'), horizontal=True, key='rdo_tvd_swap')
            if rdo_tvd_swap == 'Single':
                SLD_TVD_SINGLE = c11.number_input('Single - True Vertical Depth (Tvd)',
                                                  value=st.session_state["single_tvd_value"],
                                                  key='single_tvd_input')
                st.session_state["single_tvd_value"] = SLD_TVD_SINGLE
                c11.write('Filtered results by value')
            else:
                c121, c122 = c11.columns([0.5, 0.5])
                SLD_TVD_MIN = c121.number_input('Min -  True Vertical Depth (Tvd)',
                                                value=st.session_state["min_tvd_value"],
                                                key='min_tvd_input')
                st.session_state["min_tvd_value"] = SLD_TVD_MIN

                SLD_TVD_MAX = c122.number_input('Max -  True Vertical Depth (Tvd)',
                                                value=st.session_state["max_tvd_value"],
                                                key='max_tvd_input')
                st.session_state["max_tvd_value"] = SLD_TVD_MAX
                c11.write('Filtered results by range')
        else:
            output_md_data = c11.empty()

#
# st.markdown("---")
if SURVEYS_UPLOADED and SURVEY_DATA is not None:
    try:
        c21, c22 = st.columns([0.5, 0.5])
        temp_srvy = SURVEY_DATA.copy()
        temp_srvy['Md'] = temp_srvy['Md'].astype('int')
        temp_srvy['Tvd'] = temp_srvy['Tvd'].astype('int')
        temp_srvy = temp_srvy.reset_index(drop=True)

        # # Ensure only one slider is used at a time
        if SLD_MD_MAX > 0:
            FILTERED_SRVY_MD_DF = temp_srvy[(temp_srvy['Md'] <= SLD_MD_MAX) & (temp_srvy['Md'] >= SLD_MD_MIN)].round(2).reset_index(drop=True)
            output_md_data = c11.dataframe(FILTERED_SRVY_MD_DF.copy() ,use_container_width=True)
        if SLD_MD_SINGLE > 0:
            FILTERED_SRVY_MD_DF = temp_srvy[(temp_srvy['Md'] == SLD_MD_SINGLE)].round(2).reset_index(drop=True)
            output_md_data = c11.dataframe(FILTERED_SRVY_MD_DF.copy() ,use_container_width=True)
        if SLD_TVD_MAX > 0:
            FILTERED_SRVY_TVD_DF = temp_srvy[(temp_srvy['Tvd'] == SLD_TVD_MAX)  & (temp_srvy['Md'] >= SLD_TVD_MIN)].round(2).reset_index(drop=True)
            output_tvd_data = c11.dataframe(FILTERED_SRVY_TVD_DF.copy(), use_container_width=True)
        if SLD_TVD_SINGLE > 0:
            FILTERED_SRVY_MD_DF = temp_srvy[(temp_srvy['Tvd'] == SLD_TVD_SINGLE)].round(2).reset_index(drop=True)
            output_md_data = c11.dataframe(FILTERED_SRVY_MD_DF.copy(), use_container_width=True)

        with st.expander('Original - Survey File'):
            st.markdown('---') #todo: add to expanders
            st.markdown('#### Original - Survey File')
            st.dataframe(SURVEY_DATA_ORIGINAL, use_container_width=True)

        with st.expander('Interpolated - Survey File'):
            st.markdown('#### Interpolated - Survey File')
            st.dataframe(SURVEY_DATA, use_container_width=True)
    except:
        pass
        # st.error('Please review file standards')



