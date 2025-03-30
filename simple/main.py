import cv2 as cv

from hardware import motors, servo, camera
from target_detector import detect_targets, Target

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

def ball_collection(frame):
    results = detect_targets(frame)
    
    
def main():
    while True:
        res, frame = camera.read()

        if not res:
            continue

        ball_collection(frame)

main()