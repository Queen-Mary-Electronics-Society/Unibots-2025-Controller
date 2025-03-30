from time import sleep, time
import cv2 as cv
import numpy as np
import math

from hardware import motors, servo, camera
from target_detector import detect_targets, Target

DEBUG = True

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

ROUND_TIME = 2*60 + 30 # in seconds

BALL_APPROACH_SPEED = ...
BALL_CAPTURE_SPEED = ...
ALIGN_SPEED = ...
DISCOVERY_SPEED = ...
CAPTURE_DELAY = 1 # in s

BALL_CAPTURE_DISTANCE = 0.3 # in m?
ALIGN_TRIGGER_THRESHOLD = 0.1 # in rads?
ALIGN_DEACTIVATION_THRESHOLD = 0.03 # in rads?

PING_PONG_RADIUS = 0.020 # in m
RUGBY_HEIGHT = 0.315 / 4 # in m

ping_pong_points = np.array([
    [-1, -1, 0],  # Top-left corner
    [1, -1, 0],   # Top-right corner
    [1, 1, 0],    # Bottom-right corner
    [-1, 1, 0]    # Bottom-left corner
], dtype=np.float32) * PING_PONG_RADIUS

rugby_points = np.array([
    [0, -1, 0],  # Top-center
    [0, 0, 0],    # Middle
    [0, 1, 0],    # Bottom-center
], dtype=np.float32) * RUGBY_HEIGHT / 2

def get_angle_distance_to_ball(target: Target):
    camera_matrix = camera.get_matrix()
    
    # FIXME: classnames are different
    obj_points = None
    img_points = None
    if target.class_name == "ping-pong-ball":
        obj_points = ping_pong_points
        # FIXME: maybe incorrect direction
        img_points = np.array([
            [target.x1, target.y1],
            [target.x2, target.y1],
            [target.x2, target.y2],
            [target.x1, target.y2],
        ], dtype=np.float32)
    if target.class_name == "rugby-balls":
        obj_points = rugby_points
        mean_x = (target.x1 + target.x2) / 2
        mean_y = (target.y1 + target.y2) / 2
        img_points = np.array([
            [mean_x, target.y1],
            [mean_x, mean_y],
            [mean_x, target.y2],
        ], dtype=np.float32)

    _, _, tvec = cv.solvePnP(obj_points, img_points, camera_matrix, np.zeros((4, 1)))

    distance = np.linalg.norm(tvec)
    tx, ty, tz = tvec
    bearing = math.atan2(tx, tz)

    return bearing, distance

def find_best_ball(targets):
    # get the closest ball and most central ball
    min_score = math.inf
    best_ball = None
    for target in targets:
        angle, dist = get_angle_distance_to_ball(target)

        score = dist + abs(angle)
        if score < min_score:
            min_score = score
            best_ball = target
    
    return best_ball


def capture_action():
    print("CAPTURE")
    servo.up()
    # FIXME: maybe add a delay here? and stopping
    motors.speed(BALL_CAPTURE_SPEED)
    motors.forward()

    sleep(CAPTURE_DELAY)
    servo.down()
    # FIXME: maybe a delay here
    motors.stop()

def align(angle) -> bool:
    print("ALIGN")
    # FIXME: we need to know the direction of the angle
    motors.speed(ALIGN_SPEED)

    if abs(angle) < ALIGN_DEACTIVATION_THRESHOLD:
        return False
    
    if angle > 0:
        motors.right()
    else:
        motors.left()

    return True

is_aligning = False

def discovery():
    print("DISCOVERY")
    motors.speed(DISCOVERY_SPEED)
    motors.left()

def approach():
    print("APPROACH")
    motors.speed(BALL_APPROACH_SPEED)
    motors.forward()

def ball_collection_stage(frame):
    global is_aligning

    targets = detect_targets(frame)

    # find the closest ball to the center
    target = find_best_ball(targets)

    if target is None:
        # discovery mode
        discovery()
        return

    # find the angle and the distance
    angle, distance = get_angle_distance_to_ball(target)

    
    if is_aligning:
        # if already started aligning, continue
        is_aligning = align(angle)
    elif distance < BALL_CAPTURE_DISTANCE:
        # if the ball is close enough, go into capture mode
        capture_action()
    elif abs(angle) > ALIGN_TRIGGER_THRESHOLD:
        # if the angle is larger then threshold, align
        is_aligning = align(angle)
    else:
        # otherwise, move forward
        approach()

def debug_ball_display(frame):
    if not DEBUG:
        return
    
    targets = detect_targets(frame)
    colour = (0, 255, 0)

    for target in targets:
        angle, distance = get_angle_distance_to_ball(target)

        cv.rectangle(frame, (target.x1, target.y1), (target.x2, target.y2), colour, 2)
        cv.putText(frame, f'{target.class_name} ang: {angle:.2f} dist: {distance:.4f}', (target.x1, target.y1), cv.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
    
    cv.imshow("preview", frame)
    cv.waitKey(10)

def main():
    input("press any key to start")
    start_time = time()

    while True:
        # check if round ended
        if (time() - start_time) > ROUND_TIME:
            print("TIMEOUT")
            break

        frame = camera.get_undistorted_frame()

        if frame is None:
            continue

        ball_collection_stage(frame)
        debug_ball_display(frame)

main()