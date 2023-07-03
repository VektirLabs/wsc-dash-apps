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

# Helper functions ------------------------------------------------------------

# Create header container -----------------------------------------------------
c1 = st.container()
with c1:
    c1.header("Calculator App")
    c1.markdown("""This app is designed be the landing page for many useful
    oilfield calculations""")

# Create app container --------------------------------------------------------
c2 = st.container()
with c2:
    # Create tab layout for the Freeze Protect Ops app
    t1, t2, t3 = st.tabs(["Instructions", "Setup", "Bottoms Up Calculator"])

# Instructions Tab ------------------------------------------------------------
    with t1:
        st.markdown("#### **Instructions**")
        st.markdown("**Step 1** - Select you Rig and the current well")

# Selection & Filter Tab ------------------------------------------------------
    with t2:
        st.markdown("#### **Setup**")

# Selection & Filter Tab ------------------------------------------------------
    with t3:
        st.markdown("#### **Bottoms UP Calculator**")