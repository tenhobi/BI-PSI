from enum import Enum

from src.constants import Constants
from src.robot import Robot, Coordinates, Direction


class Controller(object):
    def __init__(self):
        # Data.
        self.robot = None
        self.state = State.USER_NAME
        self.charging = False

    def process(self, message):
        switcher = {
            1: self._process_user_name,
            2: self._process_confirmation,
            3: self._process_determining_location,
            4: self._process_determining_direction,
            5: self._process_navigating_to_area,
            6: self._process_search_message,
            7: self._process_pick_up,
        }

        method = switcher.get(int(self.state), None)
        if method is not None:
            return method(message)

        return Constants.SERVER_SYNTAX_ERROR, True

    def get_timeout(self):
        if self.charging:
            return Constants.TIMEOUT_CHARGING

        return Constants.TIMEOUT

    def _process_user_name(self, message):
        print('a1')
        a = len(message)
        if a > Constants.CLIENT_USERNAME_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('a2')
        self.robot = Robot(message)

        if self.robot.serverHash == 0:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('a3')
        self.state = State.CONFIRMATION
        return f'{self.robot.serverHash}\a\b', False

    def _process_confirmation(self, message):
        print('b1')
        if len(message) > Constants.CLIENT_CONFIRMATION_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('b2')
        try:
            input_hash = int(message)
            print('b3')
        except:
            return Constants.SERVER_LOGIN_FAILED, True

        if self.robot.clientHash != input_hash:
            return Constants.SERVER_LOGIN_FAILED, True

        print('b4')

        self.state = State.DETERMINING_LOCATION
        return Constants.SERVER_OK + Constants.SERVER_MOVE, False

    def _process_determining_location(self, message):
        print('c1')
        if len(message) > Constants.CLIENT_OK_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('c2')
        coords = Coordinates.parse(message)
        print('c3')
        if coords is None:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('c4')
        self.robot.coordinates = coords
        print(self.robot)
        self.state = State.DETERMINING_DIRECTION
        return Constants.SERVER_MOVE, False

    def _process_determining_direction(self, message):
        print('d1')
        if len(message) > Constants.CLIENT_OK_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('d2')
        coords = Coordinates.parse(message)
        if coords is None:
            return Constants.SERVER_SYNTAX_ERROR, True

        print('d3')
        # Didn't move.
        if (self.robot.coordinates.y == coords.x) and (self.robot.coordinates.y == coords.y):
            return Constants.SERVER_MOVE, False

        # Determine direction.
        if self.robot.coordinates.y > coords.y:
            self.robot.direction = Direction.NORTH
        elif self.robot.coordinates.x > coords.x:
            self.robot.direction = Direction.EAST
        elif self.robot.coordinates.y < coords.y:
            self.robot.direction = Direction.SOUTH
        elif self.robot.coordinates.x < coords.x:
            self.robot.direction = Direction.WEST
        else:
            return Constants.SERVER_SYNTAX_ERROR, True

        self.robot.coordinates = coords

        print('d4')
        if self.robot.is_in_area():
            self.state = State.SEARCH_MESSAGE
        else:
            self.state = State.NAVIGATING_TO_AREA

        print('d5')
        print(self.robot)
        return Constants.SERVER_MOVE, False

    def _process_navigating_to_area(self, message):
        if len(message) > Constants.CLIENT_OK_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        return Constants.SERVER_SYNTAX_ERROR, True

    def _process_search_message(self, message):
        if len(message) > Constants.CLIENT_OK_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        return Constants.SERVER_SYNTAX_ERROR, True

    def _process_pick_up(self, message):
        if len(message) > Constants.CLIENT_MESSAGE_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        return Constants.SERVER_SYNTAX_ERROR, True


class State(Enum):
    USER_NAME = 1
    CONFIRMATION = 2
    DETERMINING_LOCATION = 3
    DETERMINING_DIRECTION = 4
    NAVIGATING_TO_AREA = 5
    SEARCH_MESSAGE = 6
    PICK_UP = 7

    def __int__(self):
        return self.value
