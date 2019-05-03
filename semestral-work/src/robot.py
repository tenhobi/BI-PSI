from enum import Enum

from src.constants import KEY_SERVER, KEY_CLIENT


class Robot(object):
    def __init__(self, name):
        self.coordinates = (0, 0)
        self.direction = Direction.UNKNOWN

        _hash = 0
        for letter in name:
            _hash += letter

        _hash = (_hash * 1000) % 65536
        self.nameHash = _hash
        self.serverHash = (self.nameHash + KEY_SERVER) % 65536
        self.clientHash = (self.nameHash + KEY_CLIENT) % 65536


class Direction(Enum):
    UNKNOWN = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3
    EAST = 4
