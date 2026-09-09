import streamlit as st
from backend.src.auth import get_user

def is_authenticated():

    try:
        user = get_user()
        return user.user is not None

    except:
        return False