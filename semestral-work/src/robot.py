import re
from enum import Enum

from src.constants import Constants


class Robot(object):
    def __init__(self, name):
        self.name = name
        self.coordinates = None
        self.direction = Direction.UNKNOWN

        _hash = 0
        for letter in name:
            _hash += ord(letter)

        _hash = (_hash * 1000) % 65536
        self.nameHash = _hash
        self.serverHash = (self.nameHash + Constants.KEY_SERVER) % 65536
        self.clientHash = (self.nameHash + Constants.KEY_CLIENT) % 65536

    def __str__(self):
        return f'Robot "{self.name}" {self.coordinates} pointing {str(self.direction)}'

    def set_direction(self, coords):
        if self.coordinates.y > coords.y:
            self.direction = Direction.SOUTH
        elif self.coordinates.x > coords.x:
            self.direction = Direction.WEST
        elif self.coordinates.y < coords.y:
            self.direction = Direction.NORTH
        elif self.coordinates.x < coords.x:
            self.direction = Direction.EAST

    def rotate_right(self):
        if self.direction == Direction.NORTH:
            self.direction = Direction.EAST
        elif self.direction == Direction.EAST:
            self.direction = Direction.SOUTH
        elif self.direction == Direction.SOUTH:
            self.direction = Direction.WEST
        elif self.direction == Direction.WEST:
            self.direction = Direction.NORTH

    def rotate_left(self):
        self.rotate_right()
        self.rotate_right()
        self.rotate_right()


class Direction(Enum):
    UNKNOWN = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    def __str__(self):
        if self.value == 1:
            return 'north'
        elif self.value == 2:
            return 'east'
        elif self.value == 3:
            return 'south'
        elif self.value == 4:
            return 'west'
        else:
            return '???'


class Coordinates(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    @staticmethod
    def parse(data):
        match = re.match(r'^OK\s(-?\d+)\s(-?\d+)$', data)
        if match:
            return Coordinates(int(match.group(1)), int(match.group(2)))

        return None
