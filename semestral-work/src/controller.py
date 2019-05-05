from enum import Enum

from src.constants import Constants
from src.robot import Robot, Coordinates, Direction


class Controller(object):
    def __init__(self):
        # Data.
        self.robot = None
        self.state = State.USER_NAME
        self.charging = False
        self.picked = 0
        self.start_coordinates = Coordinates(-2, 2)

    def process(self, message):
        switcher = {
            1: self._process_user_name,
            2: self._process_confirmation,
            3: self._process_determining_location,
            4: self._process_navigating_to_start,
            5: self._process_search_message,
            6: self._process_pick_up,
        }

        method = switcher.get(int(self.state), None)
        if method is not None:
            return method(message)

        return Constants.SERVER_SYNTAX_ERROR, True

    def get_timeout(self):
        if self.charging:
            return Constants.TIMEOUT_RECHARGING

        return Constants.TIMEOUT

    def is_at_start(self):
        return (self.robot.coordinates.x == self.start_coordinates.x) and (
                self.robot.coordinates.y == self.start_coordinates.y)

    def should_rotate_towards_start(self):
        """
        Is rotated for moving towards start while navigating to start area.
        """

        # Navigate x.
        if self.robot.coordinates.x < self.start_coordinates.x and self.robot.direction != Direction.EAST:
            return True
        elif self.robot.coordinates.x > self.start_coordinates.x and self.robot.direction != Direction.WEST:
            return True
        elif self.robot.coordinates.x == self.start_coordinates.x:
            # Navigate y.
            if self.robot.coordinates.y < self.start_coordinates.y and self.robot.direction != Direction.NORTH:
                return True
            elif self.robot.coordinates.y > self.start_coordinates.y and self.robot.direction != Direction.SOUTH:
                return True

        return False

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
        if len(message) > Constants.CLIENT_CONFIRMATION_LENGTH or ' ' in message:
            return Constants.SERVER_SYNTAX_ERROR, True

        print(f'b2 "{message}"')
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
        self.state = State.NAVIGATING_TO_START
        return Constants.SERVER_MOVE, False

    def _process_navigating_to_start(self, message):
        if len(message) > Constants.CLIENT_OK_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        # TODO: add recharging?
        coords = Coordinates.parse(message)
        if coords is None:
            return Constants.SERVER_SYNTAX_ERROR, True

        if self.robot.direction == Direction.UNKNOWN:
            print('direction not yet set')
            # Didn't move.
            if (self.robot.coordinates.y == coords.x) and (self.robot.coordinates.y == coords.y):
                print('position didnt change')
                return Constants.SERVER_MOVE, False

            self.robot.set_direction(coords)

        self.robot.coordinates = coords

        print(self.robot)

        if self.is_at_start():
            print('!! I am at the start.')
            self.robot.rotate_right()
            self.state = State.SEARCH_MESSAGE
            return Constants.SERVER_TURN_RIGHT, False

        if self.should_rotate_towards_start():
            self.robot.rotate_right()
            return Constants.SERVER_TURN_RIGHT, False

        return Constants.SERVER_MOVE, False

    def _process_search_message(self, message):
        if len(message) > Constants.CLIENT_OK_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        coords = Coordinates.parse(message)
        if coords is None:
            return Constants.SERVER_SYNTAX_ERROR, True

        if self.robot.coordinates.x == coords.x and self.robot.coordinates.y == coords.y:
            print('!!!!!!!! STEJNE')
        self.robot.coordinates = coords

        print(self.robot)
        self.state = State.PICK_UP

        if self.picked in [4, 5, 14, 15]:
            return Constants.SERVER_TURN_RIGHT + Constants.SERVER_PICK_UP, False
        elif self.picked in [9, 10, 19, 20]:
            return Constants.SERVER_TURN_LEFT + Constants.SERVER_PICK_UP, False

        return Constants.SERVER_PICK_UP, False

    def _process_pick_up(self, message):
        if len(message) > Constants.CLIENT_MESSAGE_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        # Found it!
        if len(message) > 0:
            return Constants.SERVER_LOGOUT, True

        self.state = State.SEARCH_MESSAGE
        return Constants.SERVER_MOVE, False


class State(Enum):
    USER_NAME = 1
    CONFIRMATION = 2
    DETERMINING_LOCATION = 3
    NAVIGATING_TO_START = 4
    SEARCH_MESSAGE = 5
    PICK_UP = 6

    def __int__(self):
        return self.value
