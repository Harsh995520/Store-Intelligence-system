# Store Intelligence System using Computer Vision

## Overview

Store Intelligence System is an AI-powered retail analytics platform that uses Computer Vision to monitor customer activity inside a retail store.

The system detects customers using YOLOv8, tracks their movement across different store zones, records customer events, and generates business insights through an interactive dashboard.

---

## Features

* Customer Entry Detection
* Browsing Zone Tracking
* Checkout Detection
* Customer Journey Analysis
* Conversion Funnel Analytics
* Store Heatmap Generation
* Event Logging in JSONL Format
* FastAPI Analytics Backend
* Streamlit Dashboard

---

## Tech Stack

* Python
* YOLOv8
* OpenCV
* FastAPI
* Streamlit
* Pandas
* Plotly

---

## Project Structure

```text
Store-Intelligence-system/
│
├── app/
├── pipeline/
├── data/
├── dashboard.py
├── heatmap.py
├── README.md
├── DESIGN.md
├── CHOICES.md
├── requirements.txt
└── events.jsonl
```

---

## Workflow

1. Detect customers using YOLOv8.
2. Track movement across store zones.
3. Generate ENTRY, BROWSING, and CHECKOUT events.
4. Store events in JSONL format.
5. Serve analytics through FastAPI.
6. Visualize metrics using Streamlit.

---

## Analytics Generated

### Customer Journey

Example:

```text
VIS_1: ENTRY → BROWSING → CHECKOUT
VIS_2: ENTRY → BROWSING
```

### Funnel Metrics

* Entry Count
* Browsing Count
* Checkout Count
* Conversion Rate

### Heatmap

Visualizes customer movement and high-traffic areas inside the store.

---

## How to Run

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start FastAPI Backend

```bash
uvicorn app.main:app --reload
```

### Run Tracking Pipelines

```bash
python pipeline/entry_tracker.py
python pipeline/floor_tracker.py
python pipeline/billing_tracker.py
```

### Launch Dashboard

```bash
streamlit run dashboard.py
```

---

## Event Log Format

Events are stored in JSONL format.

Example:

```json
{"visitor_id":"VIS_1","event":"ENTRY","timestamp":"2025-06-01T10:00:00"}
{"visitor_id":"VIS_1","event":"BROWSING","timestamp":"2025-06-01T10:02:00"}
{"visitor_id":"VIS_1","event":"CHECKOUT","timestamp":"2025-06-01T10:05:00"}
```

---

## Documentation

Additional project documentation:

* DESIGN.md
* CHOICES.md

---

## Future Improvements

* Multi-camera support
* Staff exclusion
* Cloud deployment
* Real-time notifications
* Advanced customer analytics

---

## Author

Harsh Raj

Galgotias University

Purple Tech Challenge 2026 Submission
