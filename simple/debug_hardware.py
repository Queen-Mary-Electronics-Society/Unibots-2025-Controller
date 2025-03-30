import pickle
import cv2 as cv

class Motors:
    def __init__(self, *args):
        pass

    def forward(self):
        print("MOTORS FORWARD")
    
    def back(self):
        print("MOTORS FORWARD")
    
    def right(self):
        print("ROTATE RIGHT")

    def left(self):
        print("ROTATE LEFT")
    
    def speed(self, speed):
        print(f"NEW SPEED {speed}")
    
    def stop(self):
        print(f"STOPPED")
    
class Servo:
    def __init__(self, *args):
        pass

    def up(self):
        print("servo up")
    
    def down(self):
        print("servo down")

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