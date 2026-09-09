import streamlit as st

from backend.src.history import get_reports
from backend.src.dashboard import build_stats

from backend.src.analytics import (
    get_disease_distribution,
    get_predictions_by_day,
    get_community_stats,
    get_top_diseases
)

from backend.src.charts import (
    disease_distribution_chart,
    top_disease_chart,
    weekly_trend_chart
)


def show_dashboard_page():

    st.title("LeafCare Dashboard")
    st.caption(
        "AI-powered crop health monitoring and community disease intelligence."
    )

    # ==========================================================
    # Personal Analytics
    # ==========================================================

    reports = get_reports()
    
    if not reports:
        st.info("No prediction history available.")
        return

    stats = build_stats(reports)

    if not stats:
        st.warning("Unable to generate dashboard statistics.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Predictions",
            stats.get("total_predictions", 0)
        )

    with col2:
        st.metric(
            "Healthy Plants",
            stats.get("healthy", 0)
        )

    with col3:
        st.metric(
            "Diseased Plants",
            stats.get("diseased", 0)
        )

    st.divider()

    # ==========================================================
    # Charts
    # ==========================================================

    distribution = get_disease_distribution()
    top = get_top_diseases()
    trend = get_predictions_by_day()

    col1, col2 = st.columns(2)

    with col1:

        if distribution:

            st.plotly_chart(
                disease_distribution_chart(distribution),
                use_container_width=True
            )

        else:
            st.info("No disease distribution available.")

    with col2:

        if top:

            st.plotly_chart(
                top_disease_chart(top),
                use_container_width=True
            )

        else:
            st.info("No disease statistics available.")

    if trend:

        st.plotly_chart(
            weekly_trend_chart(trend),
            use_container_width=True
        )

    else:
        st.info("No trend data available.")

    st.divider()

    # ==========================================================
    # Community Analytics
    # ==========================================================

    st.subheader("Community Analytics")

    community = get_community_stats()

    if community:

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Users",
                community.get("users", 0)
            )

        with col2:
            st.metric(
                "Reports",
                community.get("reports", 0)
            )

        with col3:
            st.metric(
                "Diseases",
                community.get("diseases", 0)
            )

        with col4:
            st.metric(
                "Alerts",
                community.get("alerts", 0)
            )

    else:

        st.info("Community analytics not available.")
