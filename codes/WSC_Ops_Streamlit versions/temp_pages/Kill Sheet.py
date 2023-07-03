import streamlit as st
import pandas as pd
import numpy as np

# Set app config
st.set_page_config(
    page_title="Kill Sheet",
    # page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Create header columns
c1 = st.container()
with c1:
    c1.header("Kill Sheet Ops")
    c1.markdown("""### Coming Soon....!""")

c2 = st.container()
with c2:
    # Create tab layout for the Tally Blaster app
    t1  = st.tabs(["Instructions"])