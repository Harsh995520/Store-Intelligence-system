import os
import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
st.set_page_config(page_title="Store Intelligence", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
.metric-card {border: 1px solid rgba(128,128,128,.25); padding: 16px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("🛍️ Store Intelligence System")
st.caption("Computer-vision retail analytics powered by YOLOv8 and ByteTrack")

try:
    health = requests.get(f"{API_URL}/health", timeout=8)
    health.raise_for_status()
    st.success("Analytics API connected")
except requests.RequestException:
    st.error(f"Cannot connect to the backend at {API_URL}. Check the API service and API_URL setting.")
    st.stop()

with st.sidebar:
    st.header("Video analysis")
    uploaded = st.file_uploader(
        "Upload a store video",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        help="Use a short test clip first. Processing runs on CPU on the hosted service.",
    )
    if st.button("Process video", type="primary", disabled=uploaded is None, use_container_width=True):
        try:
            with st.spinner("Uploading video..."):
                response = requests.post(
                    f"{API_URL}/process",
                    files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "video/mp4")},
                    timeout=120,
                )
                response.raise_for_status()
                st.session_state["active_job"] = response.json()["job_id"]
                st.success("Video queued for processing.")
        except requests.RequestException as exc:
            st.error(f"Upload failed: {exc}")

    st.divider()
    st.caption("Deployment note: free hosting may sleep between visits and has limited CPU and temporary storage.")

job_id = st.session_state.get("active_job")
if job_id:
    try:
        job_response = requests.get(f"{API_URL}/jobs/{job_id}", timeout=10)
        job_response.raise_for_status()
        job = job_response.json()
        st.subheader("Current processing job")
        st.write(f"**Status:** {job['status']} — {job.get('message', '')}")
        if job["status"] in ("queued", "processing"):
            st.info("Keep this page open. Refresh the dashboard to check progress.")
        elif job["status"] == "failed":
            st.error(job.get("message", "Processing failed"))
        elif job["status"] == "completed":
            c1, c2, c3 = st.columns(3)
            c1.metric("Frames processed", job.get("frames_processed", 0))
            c2.metric("Person detections", job.get("detections", 0))
            c3.metric("Unique tracks", job.get("unique_tracks", 0))
            video_response = requests.get(f"{API_URL}{job['annotated_video']}", timeout=60)
            if video_response.ok:
                st.video(video_response.content)
            if job.get("heatmap"):
                heatmap_response = requests.get(f"{API_URL}{job['heatmap']}", timeout=30)
                if heatmap_response.ok:
                    st.image(heatmap_response.content, caption="Customer movement heatmap")
    except requests.RequestException as exc:
        st.warning(f"Could not retrieve job status: {exc}")

st.divider()
st.subheader("Store performance overview")
try:
    metrics_response = requests.get(f"{API_URL}/metrics", timeout=10)
    metrics_response.raise_for_status()
    metrics = metrics_response.json()
    a, b, c, d = st.columns(4)
    a.metric("Entries", metrics["entries"])
    b.metric("Browsing", metrics["browsing"])
    c.metric("Checkout events", metrics["checkout"])
    d.metric("Conversion rate", f"{metrics['conversion_rate']}%")

    funnel = go.Figure(go.Funnel(
        y=["Entry", "Browsing", "Checkout"],
        x=[metrics["entries"], metrics["browsing"], metrics["checkout"]],
    ))
    funnel.update_layout(title="Customer activity funnel", height=380, margin=dict(l=20, r=20, t=55, b=20))
    st.plotly_chart(funnel, use_container_width=True)

    journeys_response = requests.get(f"{API_URL}/journey", timeout=10)
    journeys_response.raise_for_status()
    journeys = journeys_response.json()
    st.subheader("Customer journeys")
    if journeys:
        rows = [{"Visitor": visitor, "Journey": " → ".join(path)} for visitor, path in journeys.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No tracking events yet. Upload a video to start an analysis.")

    st.subheader("Recent processing jobs")
    jobs_response = requests.get(f"{API_URL}/jobs", timeout=10)
    jobs_response.raise_for_status()
    jobs = jobs_response.json()
    if jobs:
        st.dataframe(pd.DataFrame(jobs), use_container_width=True, hide_index=True)
except requests.RequestException as exc:
    st.error(f"Could not load analytics: {exc}")

st.caption("Checkout events are not inferred from a generic camera clip. Add a dedicated checkout-zone rule or POS integration before interpreting conversion metrics.")
