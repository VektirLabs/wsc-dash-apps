import streamlit as st
from datetime import datetime, date, time, timedelta
import plotly.graph_objs as go
import plotly.express as px
import numpy as np

# App config ----------------------------------------------------
st.set_page_config(
    page_title=":round_pushpin: Meta Data Tagger App",
    page_icon="round_pushpin",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------------
def create_data_previewer(stmp):
    # Set the number of data points
    num_data_points = 100

    # Create a list of datetime values
    date_today = datetime.now()
    x = [date_today - timedelta(days=x) for x in range(num_data_points)]
    y = np.random.rand(num_data_points)

    # Create the Plotly line graph
    fig = px.line(x=x, y=y)

    # Define the timestamp to add the vertical line
    timestamp = datetime.now() - timedelta(days=stmp)

    # Add a vertical line at the timestamp
    fig.add_shape(
        type='line',
        x0=timestamp,
        x1=timestamp,
        y0=0,
        y1=1,
        yref='paper',
        line=dict(color='red', width=2),
    )
    fig.add_annotation(
        x=timestamp,
        y=1,
        yref='paper',
        yshift=-20, xshift=-20,
        text='Start time',
        showarrow=False,
        font=dict(size=12, color='red'),
        bgcolor='rgba(255, 255, 255, 0.7)',
        xanchor='right',
        yanchor='bottom',
    )

    # Update the

    # Update layout to expand the graph to the container width
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=25, b=5),
        title="Data Previewer",
        height=250
    )
    return fig

sb = st.sidebar

c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header(":round_pushpin: WSC - Meta Data Tagger App")
with c2:
    st.image('static/conoco_logo.png', width=225)
st.divider()
# Example data
pads = ["Pad 1", "Pad 2", "Pad 3"]
wells = ["Well A", "Well B", "Well C"]

# Create a container with 4 evenly spaced columns
col1, col2, col3, col4 = st.columns([.20, .20, .30, .30])

# Add components to each column
selected_pads = col1.multiselect("Pad", pads)
selected_well = col2.selectbox("Well", wells)
start_datetime_range = col3.slider("Select start look back range",0, 336, 0)
end_datetime_range = col4.slider("Select end look back range", 0, 336, 24)
st.divider()

event_start_datetime = st.slider("Select event start",0, end_datetime_range, 0)
# event_end_datetime = st.slider("Select event end", 0, end_datetime_range,end_datetime_range)

days_lookback = (end_datetime_range-start_datetime_range)
ch = st.plotly_chart(create_data_previewer(days_lookback), use_container_width=True)
btn = st.write(start_datetime_range)
st.divider()