import streamlit as st

def render_sidebar():

    return st.sidebar.selectbox(
        "Navigation",
        [
            "Disease Detection",
            "Prediction History",
            "Dashboard"
        ]
    )