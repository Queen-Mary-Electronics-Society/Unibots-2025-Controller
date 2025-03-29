from collections import namedtuple

import numpy as np

WorldObject = namedtuple("WorldObject", ['type', 'location'])

class Location:
    # contains both translation and rotation
    position: np.ndarray
    orientation: np.ndarray
    
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation
    
    def get_yaw():
        pass