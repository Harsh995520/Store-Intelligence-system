import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

st.title("Store Intelligence Dashboard")

st_autorefresh(
    interval=5000,  # 5 seconds
    key="refresh"
)

try:
    metrics = requests.get(
        "http://127.0.0.1:8000/metrics"
    ).json()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Entries", metrics["entries"])
    col2.metric("Browsing", metrics["browsing"])
    col3.metric("Checkout", metrics["checkout"])
    col4.metric(
        "Conversion %",
        f"{metrics['conversion_rate']}%"
    )

except Exception as e:
    st.error(
        "FastAPI server is not running on port 8000."
    )
journeys = requests.get(
    "http://127.0.0.1:8000/journey"
).json()

st.subheader("Customer Journeys")

for visitor, path in journeys.items():
    st.write(
        f"{visitor}: {' → '.join(path)}"
    )


fig = go.Figure(go.Funnel(
    y=["Entry", "Browsing", "Checkout"],
    x=[
        metrics["entries"],
        metrics["browsing"],
        metrics["checkout"]
    ]
))

st.plotly_chart(fig)

dropoff = metrics["entries"] - metrics["checkout"]

st.subheader("Business Insights")

st.write(
    f"{dropoff} visitors left without purchasing."
)

st.write(
    f"Conversion Rate: {metrics['conversion_rate']}%"
)
st.subheader("Store Heatmap")

st.image("data/heatmap.png")