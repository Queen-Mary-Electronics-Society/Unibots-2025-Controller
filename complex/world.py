from localiser import Localiser
import target_detector

from utils import Location, WorldObject

class World:
    location: Location
    objects: list[WorldObject]

    _localiser: Localiser

    def __init__(self, localiser: Localiser, target_detector):
        self._localiser = localiser
        self._target_detector = target_detector

    def update(self, frame):
        location = self._localiser.localise_self(frame)
        
