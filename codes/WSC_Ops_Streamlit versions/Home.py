import streamlit as st
import sqlite3
import pandas as pd
import numpy as np

# Set app config
st.set_page_config(
    page_title="WSC OPS",
    # page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="auto"
)

# Create header columns
c1, c2, c3 = st.columns(3)
with c3:
    c3.image("img/cpai_logo.png", width=200)

st.write("Welcome to the new WSC Ops App!")
