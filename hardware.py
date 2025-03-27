from gpiozero import Motor, Servo
import cv2

# motorboard parameters
LEFT_FWD_PIN = ...
LEFT_REV_PIN = ...

RIGHT_FWD_PIN = ...
RIGHT_REV_PIN = ...

# bridge parameters
BRIDGE_PIN = ...

left_motor = Motor(LEFT_FWD_PIN, LEFT_REV_PIN)
right_motor = Motor(RIGHT_FWD_PIN, RIGHT_REV_PIN)

bridge_servo = Servo(BRIDGE_PIN)

camera = cv2.VideoCapture(0)