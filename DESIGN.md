# Store Intelligence System - Design Document

## Overview

The Store Intelligence System is an AI-powered retail analytics platform that uses Computer Vision to track customer movement inside a store and generate business insights.

The system detects customers using YOLOv8, tracks their movement across different store zones, records events in JSONL format, and visualizes analytics through a Streamlit dashboard.

---

## System Architecture

Video Input → YOLOv8 Detection → Tracking Pipeline → Event Logger → FastAPI Backend → Streamlit Dashboard

---

## Components

### Entry Tracker

Detects customers entering the store and generates ENTRY events.

### Floor Tracker

Tracks customer movement within store browsing areas and generates BROWSING events.

### Billing Tracker

Detects customers reaching the billing area and generates CHECKOUT events.

### Event Logger

Stores customer events in JSONL format for analytics and reporting.

### FastAPI Backend

Provides APIs for metrics, customer journeys, and business insights.

### Streamlit Dashboard

Displays:

* Visitor Count
* Browsing Count
* Checkout Count
* Conversion Rate
* Customer Journeys
* Funnel Chart
* Business Insights

---

## Heatmap Generation

Customer positions collected during tracking are stored and visualized as a heatmap to identify high-traffic zones within the store.

---

## AI-Assisted Development

AI tools were used for:

* Architecture planning
* Debugging and troubleshooting
* Dashboard design guidance
* API integration assistance
* Documentation support

---

## Future Improvements

* Multi-camera support
* Real-time alerts
* Staff/customer classification
* Cloud deployment
* Advanced analytics and forecasting
