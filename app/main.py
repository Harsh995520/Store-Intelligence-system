import json
import os
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data"))).resolve()
UPLOAD_DIR = DATA_DIR / "uploads"
RESULT_DIR = DATA_DIR / "results"
EVENTS_FILE = DATA_DIR / "events.jsonl"
MODEL_PATH = Path(os.getenv("YOLO_MODEL", str(ROOT / "yolov8n.pt")))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "200"))

for folder in (DATA_DIR, UPLOAD_DIR, RESULT_DIR):
    folder.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Store Intelligence System API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Job state is in memory. On a free single-instance deployment, jobs are
# visible while this service instance is alive; uploaded files use ephemeral storage.
JOBS = {}


def append_event(visitor_id: str, event_type: str, job_id: str):
    event = {
        "event_id": str(uuid.uuid4()),
        "job_id": job_id,
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with EVENTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def read_events():
    if not EVENTS_FILE.exists():
        return []
    events = []
    with EVENTS_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def create_heatmap(points, output_path: Path):
    if not points:
        return
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    plt.figure(figsize=(9, 5))
    plt.hist2d(xs, ys, bins=40, cmap="hot")
    plt.gca().invert_yaxis()
    plt.colorbar(label="Observed detections")
    plt.title("Store Activity Heatmap")
    plt.xlabel("X position (pixels)")
    plt.ylabel("Y position (pixels)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


def run_video_job(job_id: str, video_path: Path):
    output_path = RESULT_DIR / f"{job_id}_annotated.mp4"
    heatmap_path = RESULT_DIR / f"{job_id}_heatmap.png"
    JOBS[job_id]["status"] = "processing"
    JOBS[job_id]["message"] = "Loading YOLOv8 and processing video"

    capture = None
    writer = None
    try:
        model_source = str(MODEL_PATH) if MODEL_PATH.exists() else "yolov8n.pt"
        model = YOLO(model_source)
        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise RuntimeError("Could not open the uploaded video.")

        fps = capture.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 25.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            raise RuntimeError("The uploaded video has invalid dimensions.")

        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError("Could not create the annotated output video.")

        track_frames = defaultdict(int)
        seen_visitors = set()
        positions = []
        frame_number = 0
        detections_total = 0

        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_number += 1

            result = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=[0],
                imgsz=640,
                device="cpu",
                verbose=False,
            )[0]

            if result.boxes is not None and result.boxes.id is not None:
                ids = result.boxes.id.int().cpu().tolist()
                boxes = result.boxes.xyxy.cpu().tolist()
                for track_id, box in zip(ids, boxes):
                    visitor_id = f"{job_id[:8]}_VIS_{track_id}"
                    track_frames[track_id] += 1
                    detections_total += 1
                    x1, y1, x2, y2 = box
                    positions.append(((x1 + x2) / 2, (y1 + y2) / 2))

                    if track_id not in seen_visitors:
                        seen_visitors.add(track_id)
                        append_event(visitor_id, "ENTRY", job_id)
                    elif track_frames[track_id] == 10:
                        append_event(visitor_id, "BROWSING", job_id)

            writer.write(result.plot())
            if frame_number % 30 == 0:
                JOBS[job_id]["message"] = f"Processed {frame_number} frames"

        if frame_number == 0:
            raise RuntimeError("The uploaded file contains no readable video frames.")

        create_heatmap(positions, heatmap_path)
        JOBS[job_id].update({
            "status": "completed",
            "message": "Video processing completed",
            "frames_processed": frame_number,
            "detections": detections_total,
            "unique_tracks": len(seen_visitors),
            "annotated_video": f"/jobs/{job_id}/video",
            "heatmap": f"/jobs/{job_id}/heatmap" if heatmap_path.exists() else None,
        })
    except Exception as exc:
        JOBS[job_id].update({"status": "failed", "message": str(exc)})
    finally:
        if capture is not None:
            capture.release()
        if writer is not None:
            writer.release()
        try:
            video_path.unlink(missing_ok=True)
        except OSError:
            pass


@app.get("/")
def root():
    return {
        "name": "Store Intelligence System",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_file_present": MODEL_PATH.exists()}


@app.post("/process")
async def process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
        raise HTTPException(status_code=400, detail="Upload an MP4, MOV, AVI, MKV or WebM video.")

    job_id = uuid.uuid4().hex
    destination = UPLOAD_DIR / f"{job_id}{suffix}"
    total_bytes = 0
    try:
        with destination.open("wb") as handle:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_MB * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Video exceeds the {MAX_UPLOAD_MB} MB upload limit.",
                    )
                handle.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    JOBS[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "message": "Video queued for processing",
        "filename": Path(file.filename or "video").name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    background_tasks.add_task(run_video_job, job_id, destination)
    return JOBS[job_id]


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found on this service instance.")
    return job


@app.get("/jobs/{job_id}/video")
def get_annotated_video(job_id: str):
    path = RESULT_DIR / f"{job_id}_annotated.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Annotated video is not ready.")
    return FileResponse(path, media_type="video/mp4", filename=path.name)


@app.get("/jobs/{job_id}/heatmap")
def get_heatmap(job_id: str):
    path = RESULT_DIR / f"{job_id}_heatmap.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Heatmap is not ready.")
    return FileResponse(path, media_type="image/png", filename=path.name)


@app.get("/events")
def get_events():
    return read_events()


@app.get("/metrics")
def get_metrics():
    events = read_events()
    entries = sum(event.get("event_type") == "ENTRY" for event in events)
    browsing = sum(event.get("event_type") == "BROWSING" for event in events)
    checkout = sum(event.get("event_type") == "CHECKOUT" for event in events)
    return {
        "entries": entries,
        "browsing": browsing,
        "checkout": checkout,
        "conversion_rate": round(checkout / entries * 100, 2) if entries else 0,
        "detections": len(events),
    }


@app.get("/journey")
def get_journey():
    journeys = {}
    for event in read_events():
        visitor = event.get("visitor_id", "unknown")
        journeys.setdefault(visitor, [])
        event_type = event.get("event_type")
        if event_type and (not journeys[visitor] or journeys[visitor][-1] != event_type):
            journeys[visitor].append(event_type)
    return journeys


@app.get("/jobs")
def list_jobs():
    return list(JOBS.values())[::-1]
