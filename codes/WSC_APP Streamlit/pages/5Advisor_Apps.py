import streamlit as st
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from datetime import datetime
import time
import os
from streamlit_tags import st_tags
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# App config --------------------------------------------------------
st.set_page_config(
    page_title="Advisor Apps",
    page_icon="brain",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# Global vars -------------------------------------------------------
sb = st.sidebar
USER = st.experimental_user['email']
CHAT_GPT_RES = ''
SUCCESS_MSG = ''
NOW = datetime.now()
DTTM_NOW = NOW.strftime("%m-%d-%Y %H:%M:%S")
AGENT = """You are a Petroleum & Drilling Engineering Advisor and you can answer all related questions as 
    accurately and professionally as possible. 
    Additionally, you should emphasize the Following
        - Use imperial units for any math relevant to the oil and gas industry
        - All answers should show the math and reference materials name if possible
        - Provide a quick summary at the top ob the output and the use bullet point to elaborate the details  
        - Provide a section specifically for keyword that are based on the output result 
    """

# Classes & Functions  ----------------------------------------------
def get_chatgpt_response(prompt, agent = AGENT):
    API_KEY = os.getenv('GPT4_API_KEY')
    message = AGENT + ' ' + prompt
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": message
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    try:
        if response.status_code == 200:
            print(response.json()['choices'][0]['message']['content'])
            return response.json()['choices'][0]['message']['content']
    except TypeError  as e:
        return f"""Error: Unable to get a response from the ChatGPT API {e}"""

def extract_keywords(text, keyword_phrase="Keywords:"):
    keywords_start_index = text.find(keyword_phrase)
    if keywords_start_index == -1:
        return None
    keywords_start_index += len(keyword_phrase)
    keywords_text = text[keywords_start_index:].strip()
    keywords_list = [keyword.strip() for keyword in keywords_text.split(',')]
    return keywords_list

def create_df_entry(datetime, user, user_prompt, gpt_response):
    keywords = extract_keywords(gpt_response)
    data = {
        "datetime": [datetime],
        "user": [user],
        "user_prompt": [user_prompt],
        "keywords": [keywords],
        "gpt_response": [gpt_response]
    }

    df_entry = pd.DataFrame(data)
    return df_entry

def append_to_pickle(df_entry, pickle_file="data/gpt_index.pkl"):
    if os.path.exists(pickle_file) and os.path.getsize(pickle_file) > 0:
        existing_data = pd.read_pickle(pickle_file)
        new_data = existing_data.append(df_entry, ignore_index=True)
    else:
        new_data = df_entry

    new_data.to_pickle(pickle_file)

def save_to_pickle():
    df_entry = create_df_entry(DTTM_NOW, USER, USER_INPUT, CHAT_GPT_RES)
    append_to_pickle(df_entry)

def delete_item_from_pickle(index, pickle_file="data/gpt_index.pkl"):
    if os.path.exists(pickle_file) and os.path.getsize(pickle_file) > 0:
        existing_data = pd.read_pickle(pickle_file)

        if index < len(existing_data):
            updated_data = existing_data.drop(index=index).reset_index(drop=True)
            updated_data.to_pickle(pickle_file)
            print(f"Item with index {index} has been deleted from the pickle file.")
        else:
            print(f"Error: Index {index} is out of range.")
    else:
        print("The pickle file is empty or does not exist.")

@st.cache_data
def read_pickle_to_df(pickle_file="data/gpt_index.pkl"):
    if os.path.exists(pickle_file) and os.path.getsize(pickle_file) > 0:
        df = pd.read_pickle(pickle_file)
        return df
    else:
        print("The pickle file is empty or does not exist.")
        return pd.DataFrame()

# Header section ----------------------------------------------------
c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header(":brain: WSC - Advisor Apps")
with c2:
    st.image('static/conoco_logo.png', width=225)

PE_ADV, WC_ADV , MUD_ADV = st.tabs(['Engineering Advisor', "Well Control Advisor", "Mud Advisor"])

with PE_ADV:
    c1, c2 = st.columns([0.40, 0.60])
    # Data input section ------------------------------------------------
    with c1:
        c1.markdown("##### Petroleum Engineering Advisor App")
        with c1.expander(f'GPT - Agent Information'):
            st.markdown(f'GPT - PE Advisor Agent Information: {AGENT}')
        USER_INPUT = c1.text_area("Enter your question or prompt:",height=250)

        # Send request to ChatGPT Api
        if c1.button("Submit Request"):
            c1.markdown(f'''
                    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
                    <div>
                        <h5>PE Advisor Context:</h5>
                        <ul>
                          <li><strong>User:</strong> {USER}</li>
                          <li><strong>Date time:</strong> {DTTM_NOW}</li>
                          <li><strong>Query:</strong> {USER_INPUT}</li>
                          <li>Please be patient, the PE Advisor is analyzing the question...</li>
                          <li>It should only take a few seconds for the response...</li>
                        </ul>
                    </div>
        
            ''', unsafe_allow_html=True)
            progress_bar = c1.progress(0)
            if len(USER_INPUT) == 0:
                USER_INPUT = f"""
                    Explain to the user that they need to input some text into the text box top the left.
                    Also explain who you are and how youi can help assist them as a Petroleum & Drilling Engineering 
                    Advisor.
            """
            for i in range(10):
                time.sleep(0.1)  # Sleep for 1 second
                progress_bar.progress((i + 1) / 10)  # Update the progress bar
            CHAT_GPT_RES = get_chatgpt_response(USER_INPUT)

    # Data output section -----------------------------------------------
    with c2:
        gtp_output = c2.markdown("#### Gpt - PE Advisor Response")
        c2.markdown(f'''
                {CHAT_GPT_RES}
            ''')
        if CHAT_GPT_RES is not None and len(CHAT_GPT_RES) > 1:
            if c2.button('Save response to the PE Advisor library'):
                save_to_pickle()
            SUCCESS_MSG = c2.empty()

    # Data output area --------------------------------------------------
    st.markdown('---')
    st.markdown('##### Requests Log')

    gpt_out_df = read_pickle_to_df()
    flattened_keywords = list(set([keyword for keywords_list in gpt_out_df['keywords'] if keywords_list is not None for keyword in keywords_list]))
    flattened_keywords = sorted([kw.lower() for kw in flattened_keywords])
    flattened_keywords = [kw.replace('.','') for kw in flattened_keywords]

    # Add to tags list
    keyword_tags = st_tags(
        label='#### Enter Keywords:',
        text='Press enter to add more',
        value=[],
        suggestions=flattened_keywords,
        maxtags=10,
        key="tag_filter")

    # Check if keyword_tags is empty
    if not keyword_tags:
        # If it's empty, set filtered_df to the original DataFrame
        filtered_df = gpt_out_df
    else:
        # If it's not empty, filter DataFrame where any of the keyword_tags is in the 'keywords' column
        filtered_df = gpt_out_df[gpt_out_df['keywords'].apply(
            lambda keywords: any(tag in keywords for tag in keyword_tags))]

    st.dataframe(filtered_df, use_container_width=True)

with WC_ADV:
    st.markdown('Well Control Advisor - Work in progress')

with MUD_ADV:
    st.markdown('Mud Advisor - Work in Progress')