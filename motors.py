# MOTORS.PY
# provides the interface to the drive motors and servo motor on the robot
import RPi.GPIO as GPIO

from settings import *
# on/off
# rev/fwd

def init_outputs():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)

    GPIO.output(4, True)

def motorborad_left():
    GPIO.output(LEFT_PWR_PIN, True)
    GPIO.output(LEFT_DIR_PIN, False)

    GPIO.output(RIGHT_PWR_PIN, True)
    GPIO.output(RIGHT_DIR_PIN, True)

def motorborad_right():
    pass

def motorborad_forward():
    pass

def motorborad_backward():
    pass

def motorboard_stop():
    pass

def bridge_up():
    pass

def bridge_down():
    pass
