# Store Intelligence System

A computer-vision retail analytics application using **YOLOv8**, **ByteTrack**, **FastAPI**, and **Streamlit**.

## What it does

- Upload a store video from the Streamlit dashboard.
- Detect people (COCO class 0) with YOLOv8.
- Track people across frames using the ByteTrack tracker.
- Generate an annotated MP4, person-track counts, activity events, customer journeys, and a movement heatmap.
- Expose analytics through FastAPI.

> **Metric integrity:** The current single-video workflow records an ENTRY when a track first appears and a BROWSING event after the track persists. It does not automatically infer CHECKOUT or a purchase. Checkout/conversion metrics remain zero until a dedicated checkout-zone rule or POS integration is implemented.

## Repository layout

```text
.
├── app/
│   └── main.py          # FastAPI API and video-processing worker
├── dashboard.py         # Streamlit upload and analytics dashboard
├── requirements.txt
├── render.yaml          # Render Blueprint for both services
├── yolov8n.pt           # YOLOv8 nano weights
└── data/                # Created at runtime (uploads, results, events)
```

## Run locally (Windows PowerShell)

Python 3.11 is recommended.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open a second terminal:

```powershell
.venv\Scripts\Activate.ps1
$env:API_URL="http://localhost:8000"
streamlit run dashboard.py
```

- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Deploy to Render

The included `render.yaml` defines two web services from this repository:

1. `store-intelligence-api` — FastAPI backend, YOLO inference and video processing.
2. `store-intelligence-dashboard` — Streamlit frontend configured to call the API.

Steps:

1. Push the repository to GitHub.
2. In Render, choose **New + → Blueprint** and select this repository.
3. Review the two services and deploy.
4. Open the dashboard service URL. The API is available at its own service URL and `/docs`.

The Blueprint uses the Render free plan where available. Free instances have limited CPU/RAM, can spin down, and use ephemeral filesystem storage. Use short, low-resolution clips for the first test. Files and in-memory job status are not durable across restarts or redeploys. For persistent production use, attach a persistent disk or object storage and use a durable job queue.

## API

- `GET /` — service information
- `GET /health` — health check
- `POST /process` — upload a video (multipart field: `file`)
- `GET /jobs` — recent jobs on this instance
- `GET /jobs/{job_id}` — job status
- `GET /jobs/{job_id}/video` — annotated MP4
- `GET /jobs/{job_id}/heatmap` — generated heatmap
- `GET /events` — event log
- `GET /metrics` — aggregate event metrics
- `GET /journey` — visitor journeys

## Configuration

- `API_URL`: dashboard's backend base URL (default `http://localhost:8000`)
- `DATA_DIR`: directory for uploaded videos, output files, and event log (default `./data`)
- `YOLO_MODEL`: optional path to model weights (default repository `yolov8n.pt`, otherwise Ultralytics downloads `yolov8n.pt`)
- `MAX_UPLOAD_MB`: upload limit in MB (default `200`)

## Notes

- Hosted CPU inference is slower than a local GPU. The API explicitly uses CPU for predictable deployment.
- The demo stores job state in process memory and files in the service filesystem. It is designed for a portfolio demo, not a multi-worker production system.
- The legacy standalone tracking scripts are retained for reference; the deployed upload workflow is implemented in `app/main.py`.
