import cv2 as cv
import numpy as np
from pupil_apriltags import Detector, Detection
import pickle

TAG_SIZE = 0.108 # in m

at_detector = Detector(
   families="tag36h11",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)

camera_params = pickle.load(open("tools/camera_params.pkl", 'rb'))

def detect_tags(frame, camera_matrix):
    # frame conversion and undistortion
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # extracting params from matrix into required form
    # camera_fx, camera_fy, camera_cx, camera_cy
    params = (
        camera_matrix[0, 0], 
        camera_matrix[1, 1],
        camera_matrix[0, 2], 
        camera_matrix[1, 2],
        )

    return at_detector.detect(gray_frame, 
                                estimate_tag_pose=True, 
                                camera_params=params, 
                                tag_size=TAG_SIZE)


def draw_tags(frame, detections: list[Detection]):
    DATA_COLOUR = (0,255,255)

    for detection in detections:
        # draw outline
        pts: np.ndarray = detection.corners
        pts = pts.reshape((-1,1,2)).astype(np.int32)
        cv.polylines(frame,[pts],True,DATA_COLOUR)

        # draw info
        text = f"id: {detection.tag_id}\n"
        text += f"pos: {detection.pose_t}"

        anchor_point = pts[0,0]
        line_spacing = 40
        for i, line in enumerate(text.split('\n')):
            x, y = anchor_point
            y = y + i*line_spacing

            cv.putText(
                frame, 
                line,
                (x, y),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                DATA_COLOUR,
                1,
                cv.LINE_AA
                )

def get_undistorted(frame):
    camera_matrix = camera_params["camera_matrix"]
    distortion_coefs = camera_params["distortion_coefs"]

    h,  w = frame.shape[:2]

    new_matrix, roi = cv.getOptimalNewCameraMatrix(camera_matrix, distortion_coefs, (w,h), 1, (w,h))
    undistorted_frame = cv.undistort(frame, camera_matrix, distortion_coefs, None, new_matrix)

    x, y, w, h = roi
    undistorted_frame = undistorted_frame[y:y+h, x:x+w]

    return undistorted_frame, new_matrix  


def main():
    cv.namedWindow("preview")
    vc = cv.VideoCapture(0)

    while True:
        _, frame = vc.read()
        if cv.waitKey(20) == 27: # exit on ESC
            break

        frame, camera_matrix = get_undistorted(frame)
        detections = detect_tags(frame, camera_matrix)
        draw_tags(frame, detections)
        cv.imshow("preview", frame)

    cv.destroyWindow("preview")
    vc.release()

main()