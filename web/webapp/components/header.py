import streamlit as st
from backend.src.alerts import get_disease_alerts


def render_header():
    st.markdown(
        '<div class="leafcare-brand"><span>LC</span> LeafCare <small>Plant health intelligence</small></div>',
        unsafe_allow_html=True,
    )

    alerts = get_disease_alerts()

    for alert in alerts:

        if alert["level"] == "WARNING":

            st.info(
                f"""
                Warning

                {alert['disease']}

                Detected {alert['count']} times in
                {alert['district']}
                """
            )

        elif alert["level"] == "HIGH RISK":

            st.warning(
                f"""
                High Risk

                {alert['disease']}

                Detected {alert['count']} times in
                {alert['district']}
                """
            )

        elif alert["level"] == "OUTBREAK":

            st.error(
                f"""
                Outbreak Alert

                {alert['disease']}

                Detected {alert['count']} times in
                {alert['district']}
                """
            )
