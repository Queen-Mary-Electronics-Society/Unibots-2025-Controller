# TARGET_DETECTOR.PY
# DETECTS THE POSITION OF THE TARGETS ON THE CAMERA

import cv2
from ultralytics import YOLO

MODEL_FILE = "real-world-detector.pt"
# Load a model
print("Loading a model")
model = YOLO(MODEL_FILE)
print("done")

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

print(model(frame))

cv2.destroyWindow("preview")
vc.release()