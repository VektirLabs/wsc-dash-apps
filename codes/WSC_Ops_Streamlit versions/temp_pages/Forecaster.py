import datetime
import plotly.graph_objects as go
import plotly_express as px
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid



# Set app config
st.set_page_config(
    page_title="Forecaster",
    page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Referecnes ------------------------------------------------------------------
 # https://streamlit-aggrid.readthedocs.io/en/docs/Usage.html#making-cells-editable

# Helper functions ------------------------------------------------------------
def get_forecast():
        """"
        Function to get the forecast data
            - currently produces dummy data
            - returns dataFrame
        """
        df = pd.DataFrame({'Well Name': [1, 2, 3], 'Rig Name': [4, 5, 6]})
        return df

def get_grid():
    """"
   Function to create AgGrid from df data
       - Set up Grid Options
       - returns AgGrid with Options
   """
    df = get_forecast()
    grid_options = {
        "columnDefs": [
            {"headerName": "Well Name", "field": "Well Name","editable": True,},
            {"headerName": "Rig Name","field": "col2", "editable": False, },
        ],
    }
    return AgGrid(df,grid_options)

# Create header container
c1 = st.container()
with c1:
    c1.header("Forecaster App")
    c1.markdown("""This app is designed build and forecast the Rig's 
        operations over time for planning and optimization purposes.""")

# Create app container --------------------------------------------------------
c2 = st.container()
with c2:
    # Create tab layout for the Freeze Protect Ops app
    t1, t2, t3 = st.tabs(["Instructions", "Selection & Filtering", "Operation Forecaster"])

# Instructions Tab ------------------------------------------------------------
    with t1:
        st.markdown("#### **Instructions**")
        st.markdown("**Step 1** - Select you Rig and the current well")

# Selection & Filter Tab ------------------------------------------------------
    with t2:
        st.markdown("#### **Selection and Filtering**")

# Selection & Filter Tab ------------------------------------------------------
    with t3:
        st.markdown("#### **Forecaster App**")
        grid = get_grid()
