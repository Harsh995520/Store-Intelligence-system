# Engineering Choices

## Model Selection

### Why YOLOv8?

YOLOv8 was selected because:

* High detection accuracy
* Real-time performance
* Easy integration with Python
* Strong community support

---

## Tracking Strategy

The system uses object tracking to assign unique visitor IDs and maintain customer journeys across store zones.

This enables:

* Entry tracking
* Browsing analysis
* Checkout detection
* Conversion measurement

---

## Event Schema Design

Events are stored in JSONL format.

Each event contains:

* Visitor ID
* Event Type
* Timestamp
* Zone Information

This structure supports analytics and customer journey reconstruction.

---

## API Design

FastAPI was chosen because:

* High performance
* Simple endpoint development
* Automatic API documentation
* Easy integration with Streamlit

---

## Dashboard Choice

Streamlit was selected because:

* Rapid dashboard development
* Interactive visualizations
* Simple deployment
* Native Python support

---

## Analytics Decisions

The dashboard provides:

### Conversion Funnel

Entry → Browsing → Checkout

### Customer Journey Analysis

Tracks visitor movement across store zones.

### Heatmap Analysis

Identifies popular store areas.

### Business Insights

Calculates:

* Visitor Count
* Browsing Count
* Checkout Count
* Conversion Rate

---

## Key Trade-offs

A lightweight architecture was preferred over a complex production system to ensure fast development, maintainability, and demonstration readiness for the challenge.
