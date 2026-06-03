from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.predict(
    source="../data/floor/test.mp4",
    imgsz=640,
    vid_stride=3,
    save=True,
    classes=[0]
)

print("Detection complete!")