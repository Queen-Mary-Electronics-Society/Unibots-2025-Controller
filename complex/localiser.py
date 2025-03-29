# LOCALISER.PY
# Determines the location of the robot in the arena

# TODO
# - determine orientation as well
# - fix location generation function

import cv2 as cv
import numpy as np
from pupil_apriltags import Detector, Detection

from utils import Location

TAG_SIZE = 0.100 # in m

at_detector = Detector(
   families="tag36h11",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)

def generate_tag_locations():
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

tag_positions = generate_tag_locations()

def get_tag_world_position(id):
        return tag_positions[id]

class Localiser:
    def __init__(self, camera_matrix):
        self.camera_matrix = camera_matrix

    def _detect_tags(self, frame):
        # frame conversion and undistortion
        bw_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # extracting params from matrix into required form
        # camera_fx, camera_fy, camera_cx, camera_cy
        params = (
            self.camera_matrix[0, 0], 
            self.camera_matrix[1, 1],
            self.camera_matrix[0, 2], 
            self.camera_matrix[1, 2],
            )
        
        return at_detector.detect(bw_frame, 
                                    estimate_tag_pose=True, 
                                    camera_params=params, 
                                    tag_size=TAG_SIZE)

    def _camera_location_from_detection(self, detection: Detection):
        # we utilise the knowledge of the relative positions of 
        # apriltags, in order to fix our camera in the reference
        # frame of the arena

        # FIXME: add tests on unknown tags
        tag_position = get_tag_world_position(detection.tag_id)
        camera_position = tag_position - detection.pose_t

        # TODO: we need to find the orientation of the robot as well
        return camera_position

    def _fuse_estimates(self, location_estimates: list[np.ndarray]):
        # TODO: will have to check for outliers, maybe
        # for now we will just mean it all together
        return np.mean(np.array(location_estimates), axis=0)

    def localise_self(self, frame) -> Location:
        # uses the frame to locate the current position of the robot with the
        # highest percision

        detections = self._detect_tags(frame)
        location_estimates = [self._camera_location_from_detection(detection) for detection in detections]
        location = self._fuse_estimates(location_estimates)
        
        return location