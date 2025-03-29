import time
import cv2
from ultralytics import YOLO

MODEL_FILE = "complex/real-world-detector.pt"
# Load a model
model = YOLO(MODEL_FILE)

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

# fps measurement
frame_count = 0
start = time.time_ns()
fps = -1
while True:
    ret, frame = vc.read()
    if not ret:
        continue

    results = model.track(frame, stream=True)
    for result in results:
        classes_names = result.names

        for box in result.boxes:
            # check if confidence is greater than 40 percent
            if box.conf[0] > 0.4:
                # get coordinates
                [x1, y1, x2, y2] = box.xyxy[0]
                # convert to int
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # get the class
                cls = int(box.cls[0])

                # get the class name
                class_name = classes_names[cls]

                # get the respective colour
                colour = (255, 0, 0)

                # draw the rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

                # put the class name and confidence on the image
                cv2.putText(frame, f'{classes_names[int(box.cls[0])]} {box.conf[0]:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
                
    if frame_count >= 30:
        end = time.time_ns()
        fps = 1e9 * frame_count / (end - start)
        frame_count = 0
        start = time.time_ns()
    
    if fps > 0:
        fps_label = "FPS: %.2f" % fps
        cv2.putText(frame, fps_label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    frame_count += 1

    cv2.imshow("preview", frame)

    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()