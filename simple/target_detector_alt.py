from dataclasses import dataclass
import cv2
import time
import sys
import numpy as np
import sys

#################### CONSTANTS ####################

WEIGHTS = "tools/best-198.onnx"

INPUT_WIDTH = 640
INPUT_HEIGHT = 640
# SCORE_THRESHOLD = 0.2
# NMS_THRESHOLD = 0.4
# CONFIDENCE_THRESHOLD = 0.9
# Thanks Muhie
ACTUAL_THRESHOLD = 0.4
# Usually class IDs are always like 0.9... *shrug*
CLASSID_THRESHOLD = 0.75

# The camera to stream from
CAMERA = 0

# Seconds between each AI capture
DELAY = 1
# How many seconds to increment and decrement the delay
DELAY_INCREMENT = 0.2

# How many pixels from the center when the robot should move forward
BALL_LEEWAY = 100

FONT = cv2.FONT_HERSHEY_SIMPLEX

###################################################

# Basically useless, Pi lacks Nvida GPU, may be useful for testing
# def build_model(is_cuda):
#     net = cv2.dnn.readNet(WEIGHTS)
#     if is_cuda:
#         print("Attempty to use CUDA")
#         net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#         net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
#     else:
#         print("Running on CPU")
#         net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
#         net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
#     return net

def detect(image, net):
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (INPUT_WIDTH, INPUT_HEIGHT), swapRB=True, crop=False)
    net.setInput(blob)
    preds = net.forward()
    return preds

def wrap_detection(input_image, output_data):
    class_ids = []
    confidences = []
    boxes = []

    rows = output_data.shape[0]

    image_width, image_height, _ = input_image.shape

    x_factor = image_width / INPUT_WIDTH
    y_factor =  image_height / INPUT_HEIGHT

    for r in range(rows):
        row = output_data[r]
        confidence = row[4]
        if confidence >= ACTUAL_THRESHOLD:

            classes_scores = row[5:]
            _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
            class_id = max_indx[1]
            print(classes_scores[class_id])
            if (classes_scores[class_id] > CLASSID_THRESHOLD):

                confidences.append(confidence)
                class_ids.append(class_id)

                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45) 

    return class_ids, confidences, boxes

def format_yolov5(frame):
    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result

@dataclass
class Target:
    x1: int
    y1: int
    x2: int
    y2: int

    class_name: str

CONFIDENCE_LEVEL = 0.4

net = cv2.dnn.readNet(WEIGHTS)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

CLASS_NAMES = ["ping-pong-ball", "rugby-balls"]

def detect_targets(frame):
    inputImage = format_yolov5(frame)
    outs = detect(inputImage, net)
    class_ids, confidences, boxes = wrap_detection(inputImage, outs[0])
    
    targets = list()
    for (classid, confidence, box) in zip(class_ids, confidences, boxes):
        if confidence < CONFIDENCE_LEVEL:
            continue
        
        (x, y, w, h) = box
        
        if classid == 1:
            continue
        
        target = Target(
            x,
            y,
            x+w,
            y+h,
            CLASS_NAMES[classid]
        )
        targets.append(target)
    
    return targets
        
    
