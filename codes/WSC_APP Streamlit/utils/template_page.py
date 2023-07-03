import streamlit as st

# App config ----------------------------------------------------
st.set_page_config(
    page_title="{Wellview} Apps",
    page_icon="book",
    layout="wide",
    initial_sidebar_state="collapsed"
)

sb = st.sidebar

c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header("WSC Operations Apps - {WellView}")
with c2:
    st.image('static/conoco_logo.png',width=225)