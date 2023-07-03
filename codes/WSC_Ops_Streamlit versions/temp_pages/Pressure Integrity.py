import streamlit as st
import pandas as pd
import numpy as np

# Set app config
st.set_page_config(
    page_title="Pressure Integrity Ops",
    # page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Create header columns
c1 = st.container()
with c1:
    c1.header("Pressure Integrity Ops")
    c1.markdown("""This app is designed to algorithmically interpret a
                Formation Integrity Test (FIT) or Leak-Off Test (LOT) 
                equivalent mud weight (emw)
        """)

c2 = st.container()
with c2:
    # Create tab layout for the Pressure Integrity Ops app
    t1, t2, t3, t4, t5 = st.tabs(["Instructions",
                                      "Well Data",
                                      "Surveys",
                                      "Analysis",
                                      "Finalize"
                                     ])
