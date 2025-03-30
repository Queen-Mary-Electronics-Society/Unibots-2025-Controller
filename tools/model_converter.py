from ultralytics import YOLO

model = YOLO("simple/real-world-detector.pt")
model.export(format="ncnn")
