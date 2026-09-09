import streamlit as st

from backend.src.history import get_reports
from datetime import datetime


def show_history_page():

    st.title("Prediction History")

    reports = get_reports()

    if not reports:
        st.info(
            "No reports available."
        )
        return

    for row in reports:
        st.subheader(
            row["disease_name"]
        )
        st.write(
            f"Confidence: {row['confidence']:.2f}%"
        )

        timestamp = row.get("created_at")

        if timestamp:
            from zoneinfo import ZoneInfo

            utc_time = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

            ist_time = utc_time.astimezone(
                ZoneInfo("Asia/Kolkata")
            )

            formatted_time = ist_time.strftime(
                "%d %b %Y | %I:%M %p"
)

            st.caption(
                f"Generated on {formatted_time}"
            )

        with st.expander(
            "View Report"
        ):

            st.markdown(
                row["report"]
            )

        st.divider()
