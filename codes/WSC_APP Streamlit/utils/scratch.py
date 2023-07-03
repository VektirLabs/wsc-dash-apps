# Create a button to toggle the visibility of the markdown container - Python Advisor
import streamlit as st

# Initialize the session state variable for the markdown container visibility
if 'show_markdown' not in st.session_state:
    st.session_state.show_markdown = False

# Create a button to toggle the visibility of the markdown container
toggle_button = st.button("Toggle Markdown Container")

# Update the visibility state when the button is clicked
if toggle_button:
    st.session_state.show_markdown = not st.session_state.show_markdown

# Use an if condition to display the markdown container based on the session state
if st.session_state.show_markdown:
    st.markdown("""
    ## Markdown Container
    This is a markdown container that can be toggled using the button above.
    """)