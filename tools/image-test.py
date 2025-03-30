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

def main():
    class_list = ["Ping Ball", "Rugby Ball"]
    colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]

    # Basically useless, Pi doesn't have a Nvida GPU
    # is_cuda = len(sys.argv) > 1 and sys.argv[1] == "cuda"
    # net = build_model(is_cuda)

    net = cv2.dnn.readNet(WEIGHTS)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    print("Model loaded")

    capture = cv2.VideoCapture(CAMERA)

    total_frames = 0
    delay = DELAY
    if (len(sys.argv) > 1):
        delay = int(sys.argv[1])
    last_capture_time = time.time()
    class_ids = confidences = boxes = [] 

    while True:
        _, frame = capture.read()
        if frame is None:
            print("End of stream")
            continue

        current_time = time.time()
        time_difference = current_time - last_capture_time
        fps_label = f"Delay: {delay:.1f} | Last: {time_difference:.2f} | Next: {delay-time_difference:.2f}"
        cv2.putText(frame, fps_label, (0, 20), FONT, .8, (0,0,255), 2)
        
        if time_difference >= delay:
            # Ball found flag is used to ensure the robot doesn't try and follow 2
            # balls, which could cause it to be stuck rotating between them
            ball_found = False

            inputImage = format_yolov5(frame)
            outs = detect(inputImage, net)
            class_ids, confidences, boxes = wrap_detection(inputImage, outs[0])

            total_frames += 1

            last_capture_time = current_time

            print("-------------------- DETECTED BALLS --------------------")

            if (not boxes):
                print("Nothing found, move right")

        for (classid, confidence, box) in zip(class_ids, confidences, boxes):
            # Box variable is in format [top_left_x, top_left_y, box_width, box_height]

            color = colors[int(classid) % len(colors)]
            cv2.rectangle(frame, box, color, 2)
            cv2.rectangle(frame, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
            box_text = f"{class_list[classid]} {confidence:.3f}"
            cv2.putText(frame, box_text, (box[0], box[1] - 10), FONT, .5, (0,0,255))

            box_centerx = int(box[0] + box[2] / 2)
            box_centery = int(box[1] + box[3] / 2)

            cv2.rectangle(frame, (box_centerx-5, box_centery-5, 10, 10), (0, 0, 255), -1)

            if time_difference >= delay:
                image_width, image_height, _ = inputImage.shape           
                image_centerx = image_width / 2
                image_centery = image_height / 2
                
                print(f"Ball found at center {box_centerx}, {box_centery}", end=" - ")

                # Use ball found flag to determine if we traget this ball or not
                # We do not want to target 2 balls at once
                if not ball_found:
                    ball_found = True
                    if box_centerx > image_centerx + BALL_LEEWAY:
                        print("Image to the right, move right")
                    elif box_centerx < image_centerx - BALL_LEEWAY:
                        print("Image to the left, move left")
                    else:
                        print("Looks good, move forward")
                        print("Lift servos after a second")
                        print("Close servos second before robot stops moving")
                else:
                    print("Another ball found, already tragetting a ball")

        cv2.imshow("output", frame)

        keypress = cv2.waitKey(1)
        if keypress & 0xFF == ord("q"):
            print("finished by user")
            break
        elif keypress & 0xFF == ord("["):
            delay = max(0, delay - DELAY_INCREMENT)
        elif keypress & 0xFF == ord("]"):
            delay += DELAY_INCREMENT

    print("Total frames: " + str(total_frames))

if __name__ == "__main__":
    main()
