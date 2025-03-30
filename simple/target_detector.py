from ultralytics import YOLO

model = YOLO("simple/real-world-detector.pt")

def detect_targets(frame):
    return model.track(frame, stream=True)