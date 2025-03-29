# HARWARE.PY
# Provides interface to hardware

import pickle

from gpiozero import Motor, Servo
import cv2 as cv

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

def raise_bridge():
    bridge_servo.max()

def lower_bridge():
    bridge_servo.min()

class Camera:
    def __init__(self, camera_fd=0, calibration_filename="camera_params.pkl"):
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

        return undistorted_frame, new_matrix
