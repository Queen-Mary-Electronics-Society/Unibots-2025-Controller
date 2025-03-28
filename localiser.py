# LOCALISER.PY
# Determines the location of the robot in the arena

import cv2 as cv
import numpy as np
from pupil_apriltags import Detector, Detection
import pickle

TAG_SIZE = ... # in m

at_detector = Detector(
   families="tag36h11",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)

camera_params = pickle.load(open("camera_params.pkl"))

def generate_tag_positions():
    # our reference point is North-West corner
    # East is positive x
    # South is positive z
    # Up is positive y
    # all units are in METERS

    wall_size = 2.00 # in meters
    distance_between_tags = 0.3
    distance_between_islands = 0.5
    tags_per_island = 3

    directions = np.array([
        [1, 0, 0],
        [0, 0, 1],
        [-1, 0, 0],
        [0, 0, -1],
    ])

    corners = directions * wall_size
    corners = np.cumsum(corners, axis=0)
    corners = np.roll(corners, 1, axis=0)

    positions = []
    for corner, direction in zip(corners, directions):
        for idx in range(tags_per_island * 2):
            island_num = idx // tags_per_island
            local_idx = idx % tags_per_island
            tag_pos = local_idx * distance_between_tags + distance_between_tags / 2
            
            if island_num == 1:
                tag_pos += (tags_per_island - 1) * distance_between_tags + distance_between_islands

            tag_pos = direction * tag_pos + corner
            positions.append(tag_pos)
    
    return positions

tag_positions = generate_tag_positions()

def detect_tags(frame):
    # frame conversion and undistortion
    camera_matrix = camera_params["camera_matrix"]
    distortion_coefs = camera_params["distortion_coefs"]
    
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    h,  w = gray_frame.shape[:2]

    new_matrix = cv.getOptimalNewCameraMatrix(camera_matrix, distortion_coefs, (w,h), 1, (w,h))
    undistorted_frame = cv.undistort(gray_frame, camera_matrix, distortion_coefs, None, new_matrix)    

    return at_detector.detect(undistorted_frame, 
                                estimate_tag_pose=True, 
                                camera_params=camera_matrix, 
                                tag_size=TAG_SIZE)

def get_tag_world_position(id):
    return tag_positions[id]

def camera_location_from_detection(detection: Detection):
    # we utilise the knowledge of the relative positions of 
    # apriltags, in order to fix our camera in the reference
    # frame of the arena

    # FIXME: add tests on unknown tags
    tag_position = get_tag_world_position(detection.tag_id)
    camera_position = tag_position - detection.pose_t

    # TODO: we need to find the orientation of the robot as well
    return camera_position

def fuse_estimates(location_estimates: list[np.ndarray]):
    # TODO: will have to check for outliers, maybe
    # for now we will just mean it all together
    return np.mean(np.array(location_estimates), axis=0)

def localise_self(frame) -> np.ndarray:
    # uses the frame to locate the current position of the robot with the
    # highest percision

    detections = detect_tags(frame)
    location_estimates = [camera_location_from_detection(detection) for detection in detections]
    location = fuse_estimates(location_estimates)
    
    return location