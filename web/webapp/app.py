import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))



import streamlit as st

from web.webapp.views.auth_page import show_auth_page
from web.webapp.views.detection_page import show_detection_page
from web.webapp.views.history_page import show_history_page
from web.webapp.views.dashboard_page import show_dashboard_page

from web.webapp.components.header import render_header

from backend.src.auth import get_user, sign_out


def apply_leafcare_theme():
    """Apply presentation-only styling shared by every LeafCare page."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

            :root {
                --leafcare-forest: #132A13;
                --leafcare-deep: #31572C;
                --leafcare-green: #4F772D;
                --leafcare-olive: #90A955;
                --leafcare-mist: #ECF39E;
                --leafcare-surface: #1A3118;
                --leafcare-text: #F8FAF0;
            }

            .stApp {
                background: radial-gradient(circle at top right, #31572C 0%, #1A3118 43%, #132A13 100%);
                color: var(--leafcare-text);
                font-family: 'DM Sans', sans-serif;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #132A13 0%, #31572C 100%);
            }

            [data-testid="stSidebar"] * { color: #F8FAF0; }
            [data-testid="stSidebar"] [data-baseweb="select"] > div {
                background-color: rgba(255, 255, 255, 0.13);
                border-color: rgba(236, 243, 158, 0.5);
            }

            h1, h2, h3 {
                color: var(--leafcare-mist) !important;
                font-family: 'Fraunces', serif !important;
            }
            h1 { font-weight: 700 !important; letter-spacing: -0.04em; }

            p, label, [data-testid="stCaptionContainer"] {
                color: var(--leafcare-text) !important;
            }

            [data-baseweb="input"] > div,
            [data-baseweb="select"] > div {
                background: rgba(19, 42, 19, 0.72) !important;
                border-color: rgba(144, 169, 85, 0.58) !important;
            }

            [data-baseweb="input"] input,
            [data-baseweb="select"] * {
                color: var(--leafcare-text) !important;
            }

            .stButton > button {
                background: var(--leafcare-green);
                color: #FFFFFF;
                border: 0;
                border-radius: 10px;
                font-weight: 700;
                padding: 0.6rem 1rem;
                transition: 0.2s ease;
            }

            .stButton > button:hover {
                background: var(--leafcare-deep);
                box-shadow: 0 5px 14px rgba(19, 42, 19, 0.22);
                transform: translateY(-1px);
            }

            [data-testid="stMetric"] {
                background: rgba(19, 42, 19, 0.62);
                border: 1px solid rgba(144, 169, 85, 0.3);
                border-radius: 14px;
                padding: 1rem;
                box-shadow: 0 3px 12px rgba(19, 42, 19, 0.07);
            }

            [data-testid="stMetric"] * { color: var(--leafcare-text) !important; }

            [data-testid="stFileUploader"] {
                background: rgba(19, 42, 19, 0.62);
                border: 1px dashed var(--leafcare-olive);
                border-radius: 14px;
                padding: 0.75rem;
            }

            [data-testid="stFileUploader"] * { color: var(--leafcare-text) !important; }

            [data-testid="stExpander"], [data-testid="stTabs"] button {
                background: rgba(19, 42, 19, 0.45);
                border-color: rgba(144, 169, 85, 0.28);
                color: var(--leafcare-text) !important;
            }

            .leafcare-brand {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                margin: 0.15rem 0 1.6rem;
                color: var(--leafcare-mist);
                font-size: 1.05rem;
                font-weight: 800;
                letter-spacing: 0.02em;
            }

            .leafcare-brand span {
                display: grid;
                place-items: center;
                width: 2.1rem;
                height: 2.1rem;
                border-radius: 50%;
                background: var(--leafcare-forest);
                color: var(--leafcare-mist);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    #---------- Page Config ----------

    st.set_page_config(
        page_title="LeafCare",
        page_icon="L",
        layout="wide"
    )

    apply_leafcare_theme()

    #---------- Authentication Check ----------

    try:
        current_user = get_user()

        authenticated = (
            current_user is not None
            and current_user.user is not None
        )

    except Exception:
        authenticated = False
        current_user = None


    #---------- Login Page ----------

    if not authenticated:
        show_auth_page()
        st.stop()


    #---------- Sidebar ----------

    st.sidebar.success(
        f"Logged in as\n\n{current_user.user.email}"
    )

    page = st.sidebar.selectbox(
        "Navigation",
        [
            "Disease Detection",
            "My Reports",
            "Dashboard"
        ]
    )

    if st.sidebar.button("Logout"):
        sign_out()
        st.rerun()


    #---------- Header ----------

    render_header()


    #---------- Routing ----------

    if page == "Disease Detection":
        show_detection_page()

    elif page == "My Reports":
        show_history_page()

    elif page == "Dashboard":
        show_dashboard_page()

if __name__ == "__main__":
    main()
