from dataclasses import dataclass

from ultralytics import YOLO

model = YOLO("simple/real-world-detector.pt")

@dataclass
class Target:
    x1: int
    y1: int
    x2: int
    y2: int

    class_name: str

CONFIDENCE_LEVEL = 0.4

def detect_targets(frame) -> list[Target]:
    results = model.track(frame, stream=True)

    targets = list()
    for result in results:
        classes_names = result.names

        for box in result.boxes:
            if box.conf[0] < CONFIDENCE_LEVEL:
                continue

            (x1, y1, x2, y2) = box.xyxy[0]
            # convert to int
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # get the class
            cls = int(box.cls[0])

            # get the class name
            class_name = classes_names[cls]

            target = Target(x1, y1, x2, y2, class_name)
            targets.append(target)
    
    return targets
