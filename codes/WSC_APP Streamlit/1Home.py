import streamlit as st
from utils import queries as qry
from dotenv import load_dotenv
import keyboard as kb
from PIL import ImageGrab, Image

# load_dotenv()

# App config ----------------------------------------------------
st.set_page_config(
    page_title="WSC Apps",
    page_icon="fire",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# Images links
conoco_logo = "https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/conoco_logo.png"
wv_logo = "https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/WV_logo.PNG"
schm_logo = 'https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/schematics.jpg'
intp_logo = 'https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/interpolator.png'
fpa_logo = 'https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/fpa.png'
gpt_logo = 'https://bvlamqp3.conocophillips.net/thunt1/wsc_apps/-/raw/main/static/gpt4_logo.png'

# Sidebar
sb = st.sidebar

# Header section
c1, c2, c3 = st.columns([0.84, 0.15, 0.01])
with c1:
    st.markdown("### :fire: **WSC Apps** - Home")
with c2:
    st.image(conoco_logo, width=225)
with c3:
    res = c3.button(':camera:')
    if res:
        kb.press_and_release('Ctrl+Shift+S')
        # im = ImageGrab.grabclipboard()
        # im.show()

b1, b2, b3 = st.columns([0.33, 0.33, 0.33])
header_html = '<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">'

# Cards row 1 ------------------------------------------------------
wv_card_name = 'Wellview Apps'
wv_card = b1.markdown(f"""{header_html}
    <div class="w3-center"><h3><b>{wv_card_name}</b></h3>
    <p>Wellview Apps - Well handover, Docs, etc.</p></div>
    <div class="w3-card-4 w3-margin w3-center">
        <a href="/Wellview_Apps">
            <img src="{wv_logo}" alt="Wellview Apps" height="200px">
        </a>
        <div class="w3-container w3-center">
            <a href="/Wellview_Apps" class="w3-button">Wellview Apps</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

schm_card_name = 'Schematic App'
schematic_card = b2.markdown(f"""{header_html}
    <div class="w3-center"><h3><b>{schm_card_name}</b></h3>
    <p>Build a well schematic app </p></div>
    <div class="w3-card-4 w3-margin w3-center">
        <a href="/Schematic_Apps">
            <img src="{schm_logo}" alt="{schm_card_name}" height="200px">
        </a>
        <div class="w3-container w3-center">
            <a href="/Schematic_Apps" class="w3-button">{schm_card_name}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

fpa_card_name = 'Freeze Protect App'
fpa_card = b3.markdown(f"""{header_html}
    <div class="w3-center"><h3><b>{fpa_card_name}</b></h3>
    <p>Freeze Protection Analysis App</p></div>
    <div class="w3-card-4 w3-margin w3-center">
        <a href="/Freeze_Protect_App">
            <img src="{fpa_logo}" alt="{fpa_card_name}" height="200px">
        </a>
        <div class="w3-container w3-center">
            <a href="/Freeze_Protect_App" class="w3-button">{fpa_card_name}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Cards row 2 ------------------------------------------------------
intp_card_name = 'Interpolator App' #
intp_card = b1.markdown(f"""{header_html}
    <div class="w3-center"><h3><b>{intp_card_name}</b></h3>
    <p>Interpolate your survey file for analysis</p></div>
    <div class="w3-card-4 w3-margin w3-center">
        <a href="/Interpolator_App">
            <img src="{intp_logo}" alt="{intp_card_name}" height="200px">
        </a>
        <div class="w3-container w3-center">
            <a href="/Interpolator_App" class="w3-button">{intp_card_name}</a>
        </div>
    </div>
    """,unsafe_allow_html=True)

gpt_card_name = 'Advisor Apps' #
gpt_card = b2.markdown(f"""{header_html}
    <div class="w3-center"><h3><b>{gpt_card_name}</b></h3>
    <p>Pre-programmed GPT Advisor Apps</p></div>
    <div class="w3-card-4 w3-margin w3-center">
        <a href="/Advisor_Apps">
            <img src="{gpt_logo}" alt="{gpt_card_name}" height="200px">
        </a>
        <div class="w3-container w3-center">
            <a href="/Advisor_Apps" class="w3-button">{gpt_card_name}</a>
        </div>
    </div>
    """ ,unsafe_allow_html=True)