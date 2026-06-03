from app.app_manager import emit_event
from ultralytics import YOLO
import supervision as sv

model = YOLO("yolov8n.pt")

tracker = sv.ByteTrack()

results = model.predict(
    source="../data/floor/CAM 2.mp4",
    stream=True,
    classes=[0],
    imgsz=640,
    vid_stride=3
)
seen_ids = set()
for result in results:

    detections = sv.Detections.from_ultralytics(result)

    detections = tracker.update_with_detections(
        detections
    )
    for xyxy in detections.xyxy:

        x1, y1, x2, y2 = xyxy

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        with open("../data/positions.csv", "a") as f:
            f.write(f"{center_x},{center_y}\n")

    print("Track IDs:", detections.tracker_id)
    if detections.tracker_id is not None:

        for track_id in detections.tracker_id:

            if track_id not in seen_ids:

                seen_ids.add(track_id)

                emit_event(
                    visitor_id=f"VIS_{track_id}",
                    event_type="BROWSING"
                )

    print("Track IDs:", detections.tracker_id)