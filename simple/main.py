import cv2 as cv

from hardware import camera
from target_detector import detect_targets

# question is: our ball model runs at 1 fps best case,
# how will we be able to do any realtime control with it?
# will go slowly??

# so, basically.
# we have two modes, one is ball collection mode, the other one is parking mode
# the modes activate depending on how much time is left in the round

# the ball collection mode detects a ball, and locks in on it, 
# it tries to keep the ball in the centre of the frame while moving
# after collecting a ball, the robot goes into discovery, trying to detect any more
# nearby balls and lock on them
# we can also implement a safeguard by ensuring that the robot doesn't get too close to other
# robot's parking area

# in parking mode, the robot rotates to detect the position of the home tags, and moves 
# to them trying to keep them at the centre
# once it got close enough to them, it shutdowns

CONFIDENCE_LEVEL = 0.4

def ball_collection(frame):
    results = detect_targets(frame)

    for result in results:
        classes_names = result.names

        for box in result.boxes:
            # check if confidence is greater than 40 percent
            if box.conf[0] < CONFIDENCE_LEVEL:
                continue

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
            cv.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

            # put the class name and confidence on the image
            cv.putText(frame, f'{classes_names[int(box.cls[0])]} {box.conf[0]:.2f}', (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
        
        cv.imshow('preview', frame)
        cv.waitKey(20)
    
def main():
    while True:
        res, frame = camera.read()

        if not res:
            continue

        ball_collection(frame)

main()