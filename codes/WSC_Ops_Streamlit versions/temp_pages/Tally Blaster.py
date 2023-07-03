import streamlit as st
import pandas as pd
import numpy as np

# Set app config
st.set_page_config(
    page_title="Tally Blaster",
    # page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Create header columns
c1 = st.container()
with c1:
    c1.header("Tally Blaster")
    c1.markdown("""This app is designed to streamline the calculations 
        necessary for most tubular management at CPAI
        """)

c2 = st.container()
with c2:
    # Create tab layout for the Tally Blaster app
    t1  = st.tabs(["Instructions"])