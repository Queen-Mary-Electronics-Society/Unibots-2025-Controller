from time import sleep

from hardware import motors, servo

SPEED = 50
FORWARD_DELAY = 4

def main():
    # open gate
    servo.up()
    # go forward
    motors.speed(SPEED)
    motors.forward()
    sleep(FORWARD_DELAY)

    # close gate
    servo.down()
    # stop
    motors.stop()
    sleep(1)
    # go backward
    motors.back()
    sleep(FORWARD_DELAY + 1)

    print("We are done here")
