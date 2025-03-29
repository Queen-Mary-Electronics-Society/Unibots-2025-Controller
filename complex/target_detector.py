import cv2
from ultralytics import YOLO

from utils import Location

MODEL_FILE = "real-world-detector.pt"

class TargetDetector:
    def __init__(self, camera_matrix):
        self._camera_matrix = camera_matrix
        self._model = YOLO(MODEL_FILE)
    
    def detect_objects(self, frame, location: Location):
        results = self._model.track(frame, stream=True) # FIXME: can potentially break on low fps
        for result in results:
            pass
