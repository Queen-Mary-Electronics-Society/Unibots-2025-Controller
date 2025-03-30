import RPi.GPIO as GPIO
import pickle
import cv2 as cv

GPIO.setmode(GPIO.BCM)

class Motors():
    def __init__(self, enA, in1, in2, enB, in3, in4):
        self.enable_a = enA
        self.enable_b = enB

        self.in_1 = in1
        self.in_2 = in2
        self.in_3 = in3
        self.in_4 = in4

        GPIO.setup(self.enable_a,GPIO.OUT)
        GPIO.setup(self.enable_b,GPIO.OUT)

        GPIO.setup(self.in_1,GPIO.OUT) # set gpio pins as outputs
        GPIO.setup(self.in_2,GPIO.OUT)
        GPIO.setup(self.in_3,GPIO.OUT)
        GPIO.setup(self.in_4,GPIO.OUT)


        self.stop()
        self.left=GPIO.PWM(self.enable_a,1000)
        self.right=GPIO.PWM(self.enable_b,1000) # set pwm freq

        self.left.start(25)
        self.right.start(25)

    def forward(self):
        GPIO.output(self.in_1,GPIO.HIGH)
        GPIO.output(self.in_2,GPIO.LOW)

        GPIO.output(self.in_3,GPIO.LOW)
        GPIO.output(self.in_4,GPIO.HIGH)
    
    def back(self):
        GPIO.output(self.in_1,GPIO.LOW)
        GPIO.output(self.in_2,GPIO.HIGH)

        GPIO.output(self.in_3,GPIO.HIGH)
        GPIO.output(self.in_4,GPIO.LOW)

    def right(self): 
        GPIO.output(self.in_1,GPIO.HIGH)
        GPIO.output(self.in_2,GPIO.LOW)

        GPIO.output(self.in_3,GPIO.HIGH)
        GPIO.output(self.in_4,GPIO.LOW)
    
    def left(self):
        GPIO.output(self.in_1,GPIO.LOW)
        GPIO.output(self.in_2,GPIO.HIGH)

        GPIO.output(self.in_3,GPIO.LOW)
        GPIO.output(self.in_4,GPIO.HIGH)

    def stop(self):
        GPIO.output(self.in_1, GPIO.LOW)
        GPIO.output(self.in_2, GPIO.LOW)
        GPIO.output(self.in_3, GPIO.LOW)
        GPIO.output(self.in_4, GPIO.LOW)

    def speed(self, speed):
        self.left.ChangeDutyCycle(speed)
        self.right.ChangeDutyCycle(speed)

    def coast(self):
        self.left.ChangeDutyCycle(0)
        self.right.ChangeDutyCycle(0)

class Servo:
    def __init__(self, pin):
        self.pin = pin

        GPIO.setup(pin, GPIO.OUT)
        # 50 Hz (20 ms PWM period)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(7)
    
    def max(self):
        self.pwm.ChangeDutyCycle(12.0) # rotate to 180 degrees

    """
    rotate to 90 degrees
    """
    def up(self):
        self.pwm.ChangeDutyCycle(7.0) 


    # Zero the servo
    def down(self):
        self.pwm.ChangeDutyCycle(2.0) 

class Camera:
    def __init__(self, camera_fd=0, calibration_filename="simple/camera_params.pkl"):
        self._camera_stream = cv.VideoCapture(camera_fd)
        
        camera_parameters = pickle.load(open(calibration_filename, 'rb'))

        self._raw_camera_matrix = camera_parameters["camera_matrix"]
        self._distortion_coefs = camera_parameters["distortion_coefs"]

        self.frame_size = None
        
    def get_raw_frame(self) -> cv.Mat | None:
        res, frame = self._camera_stream.read()

        if not res:
            return None

        # update frame size on first start
        if self.frame_size is None:
            self.frame_size = frame.shape[:2]
        
        return frame

    def get_undistorted_frame(self):
        frame = self.get_raw_frame()

        h,  w = self.frame_size

        # undistorting
        new_matrix, roi = cv.getOptimalNewCameraMatrix(self._raw_camera_matrix, self._distortion_coefs, (w,h), 1, (w,h))
        undistorted_frame = cv.undistort(frame, self._raw_camera_matrix, self._distortion_coefs, None, new_matrix)

        # cropping
        x, y, w, h = roi
        undistorted_frame = undistorted_frame[y:y+h, x:x+w]

        self.camera_matrix = new_matrix

        return undistorted_frame
    
    def get_matrix(self):
        return self.camera_matrix
    

motors = Motors(25, 24, 23, 11, 10, 9)
servo = Servo(17)
camera = Camera()