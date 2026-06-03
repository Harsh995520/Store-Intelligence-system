# Store Intelligence System

## Overview
An AI-powered retail analytics system that tracks customer movement inside a store using YOLOv8 and Computer Vision.

## Features
- Entry Detection
- Browsing Detection
- Checkout Detection
- Customer Journey Tracking
- Heatmap Generation
- Conversion Funnel Analytics
- Streamlit Dashboard

## Tech Stack
- Python
- YOLOv8
- FastAPI
- Streamlit
- OpenCV
- Supervision

## Run
pip install -r requirements.txt

uvicorn app.main:app --reload

streamlit run dashboard.py
