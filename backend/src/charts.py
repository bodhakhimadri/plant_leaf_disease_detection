import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def weekly_trend_chart(data):

    df = pd.DataFrame({
        "Date": list(data.keys()),
        "Predictions": list(data.values())
    })

    fig = px.line(
        df,
        x="Date",
        y="Predictions",
        markers=True,
        title="Predictions in Last 7 Days"
    )

    fig.update_layout(
        template="plotly_white",
        height=350
    )

    return fig

def disease_distribution_chart(data):

    df = pd.DataFrame({
        "Disease": list(data.keys()),
        "Count": list(data.values())
    })

    fig = px.pie(
        df,
        names="Disease",
        values="Count",
        hole=0.45,
        title="Disease Distribution"
    )

    fig.update_layout(
        template="plotly_white",
        height=400
    )

    return fig

def top_disease_chart(data):

    df = pd.DataFrame(
        data,
        columns=[
            "Disease",
            "Count"
        ]
    )

    fig = px.bar(
        df,
        x="Disease",
        y="Count",
        text="Count",
        title="Top Diseases"
    )

    fig.update_layout(
        template="plotly_white",
        height=350
    )

    return fig