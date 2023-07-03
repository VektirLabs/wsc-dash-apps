import streamlit as st
import keyboard as kb

# App config ----------------------------------------------------
st.set_page_config(
    page_title="Wellview Apps",
    page_icon="streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Images links
conoco_logo = "https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/conoco_logo.png"
wv_logo = "https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/WV_logo.PNG"

# Create sidebar
sb = st.sidebar

# Header section
c1, c2, c3 = st.columns([0.84, 0.15, 0.01])
with c1:
    st.markdown("### :book: WSC - Wellview App")
with c2:
    st.image(conoco_logo, width=225)
with c3:
    res = c3.button(':camera:')
    if res:
        kb.press_and_release('Ctrl+Shift+S')

#Add tab sections to seperate app

tab1, tab2, tab3, tab4 = st.tabs(["Instructions", "Daily Review", "Codes Cheat Sheet", "Well Handover Review"])

with tab1:
    st.subheader("Instructions")
    st.markdown(f""" Please review the following instructions
        1 - Be awesome
    """)
with tab2:
    st.subheader("Daily Reviews")

    st.subheader("Wellview FOT | LOT Entry Report")
    st.image('static/fit_pic1.png')
    st.image('static/fit_pic2.png')

with tab3:
    st.subheader("Well Handover Report")
    st.write("""Please review the following well handover report at the end of every well to ensure that 
    your current well is properly filled out and set up for the post Rig teams""")
    st.image('static/wellview_cheat_codes.png')

with tab4:
    st.subheader("Well Handover Report")
    st.write("""Please review the following well handover report at the end of every well to ensure that 
    your current well is properly filled out and set up for the post Rig teams""")
    st.image('static/well_handover_1.png')
    st.image('static/well_handover_2.png')
    st.image('static/well_handover_3.png')