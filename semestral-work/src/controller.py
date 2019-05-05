import re
from enum import Enum

from src.constants import Constants
from src.robot import Robot, Coordinates, Direction


class Controller(object):
    def __init__(self):
        # Data.
        self.robot = None
        self.state = State.USER_NAME
        self.recharging = False
        self.picked = 0
        self.start_coordinates = Coordinates(-2, 2)

    def process(self, message):
        if self.recharging:
            match = re.match(f'^{Constants.CLIENT_FULL_POWER}$', message)
            self.recharging = False

            if not match:
                return Constants.SERVER_LOGIC_ERROR, True

            return Constants.SERVER_INTERNAL_FULL_POWER, False
        else:
            match = re.match(f'^{Constants.CLIENT_RECHARGING}$', message)
            if match:
                print('RECHARGING!!')
                self.recharging = True
                return Constants.SERVER_INTERNAL_RECHARGING, False

        switcher = {
            1: self._process_user_name,
            2: self._process_confirmation,
            3: self._process_determining_location,
            4: self._process_navigating_to_start,
            5: self._process_search_message,
            6: self._process_pick_up,
        }

        print('---', self.state)

        method = switcher.get(int(self.state), None)
        if method is not None:
            return method(message)

        return Constants.SERVER_SYNTAX_ERROR, True

    def get_timeout(self):
        if self.recharging:
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
        if self.is_message_long(message):
            return Constants.SERVER_SYNTAX_ERROR, True

        self.robot = Robot(message)

        if self.robot.serverHash == 0:
            return Constants.SERVER_SYNTAX_ERROR, True

        self.state = State.CONFIRMATION
        return f'{self.robot.serverHash}\a\b', False

    def _process_confirmation(self, message):
        if self.is_message_long(message) or ' ' in message:
            return Constants.SERVER_SYNTAX_ERROR, True

        try:
            input_hash = int(message)
        except:
            return Constants.SERVER_LOGIN_FAILED, True

        if self.robot.clientHash != input_hash:
            return Constants.SERVER_LOGIN_FAILED, True

        self.state = State.DETERMINING_LOCATION
        return Constants.SERVER_OK + Constants.SERVER_MOVE, False

    def _process_determining_location(self, message):
        if self.is_message_long(message):
            return Constants.SERVER_SYNTAX_ERROR, True

        coords = Coordinates.parse(message)
        if coords is None:
            return Constants.SERVER_SYNTAX_ERROR, True

        self.robot.coordinates = coords
        print(self.robot)
        self.state = State.NAVIGATING_TO_START
        return Constants.SERVER_MOVE, False

    def _process_navigating_to_start(self, message):
        if self.is_message_long(message):
            return Constants.SERVER_SYNTAX_ERROR, True

        # TODO: add recharging?
        coords = Coordinates.parse(message)
        if coords is None:
            return Constants.SERVER_SYNTAX_ERROR, True

        if self.robot.direction == Direction.UNKNOWN:
            print('Direction not yet set.')
            # Didn't move.
            if (self.robot.coordinates.y == coords.x) and (self.robot.coordinates.y == coords.y):
                print("Robot's position didn't change.")
                return Constants.SERVER_MOVE, False

            self.robot.set_direction(coords)

        self.robot.coordinates = coords

        print(self.robot)

        if self.is_at_start():
            print('I am at the start.')

            if self.robot.direction == Direction.NORTH:
                self.robot.rotate_right()
                self.state = State.SEARCH_MESSAGE
                return Constants.SERVER_TURN_RIGHT, False
            elif self.robot.direction == Direction.SOUTH:
                self.robot.rotate_left()
                self.state = State.SEARCH_MESSAGE
                return Constants.SERVER_TURN_LEFT, False
            elif self.robot.direction == Direction.EAST:
                self.robot.rotate_left()
                return Constants.SERVER_TURN_LEFT, False
            elif self.robot.direction == Direction.WEST:
                self.robot.rotate_right()
                return Constants.SERVER_TURN_RIGHT, False
            else:
                print('WTF how?')
                return Constants.SERVER_LOGIC_ERROR, True

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

        # Is this useful?
        if self.robot.coordinates.x == coords.x and self.robot.coordinates.y == coords.y:
            print('!!!!!!!! STEJNE')

        self.robot.coordinates = coords

        print(self.robot)

        if self.picked in [4, 14] and self.robot.direction == Direction.EAST:
            self.robot.rotate_right()
            return Constants.SERVER_TURN_RIGHT, False
        if self.picked in [5, 15] and self.robot.direction == Direction.SOUTH:
            self.robot.rotate_right()
            return Constants.SERVER_TURN_RIGHT, False
        elif self.picked in [9, 19] and self.robot.direction == Direction.WEST:
            self.robot.rotate_left()
            return Constants.SERVER_TURN_LEFT, False
        elif self.picked in [10, 20] and self.robot.direction == Direction.SOUTH:
            self.robot.rotate_left()
            return Constants.SERVER_TURN_LEFT, False

        self.state = State.PICK_UP
        return Constants.SERVER_PICK_UP, False

    def _process_pick_up(self, message):
        if len(message) > Constants.CLIENT_MESSAGE_LENGTH:
            return Constants.SERVER_SYNTAX_ERROR, True

        self.picked += 1

        # Found it!
        if len(message) > 0:
            print(f"Secret message found! '{message}'")
            return Constants.SERVER_LOGOUT, True

        self.state = State.SEARCH_MESSAGE
        return Constants.SERVER_MOVE, False

    def get_state_message_limit(self):
        if self.state == State.USER_NAME:
            return Constants.CLIENT_USERNAME_LENGTH
        elif self.state == State.CONFIRMATION:
            return Constants.CLIENT_CONFIRMATION_LENGTH
        elif self.state == State.DETERMINING_LOCATION:
            return Constants.CLIENT_OK_LENGTH
        elif self.state == State.NAVIGATING_TO_START:
            return Constants.CLIENT_OK_LENGTH
        elif self.state == State.SEARCH_MESSAGE:
            return Constants.CLIENT_OK_LENGTH
        elif self.state == State.PICK_UP:
            return Constants.CLIENT_MESSAGE_LENGTH
        else:
            print('WTF? In what state are you in?')
            return 0

    def is_message_long(self, message):
        return len(message) > self.get_state_message_limit()


class State(Enum):
    USER_NAME = 1
    CONFIRMATION = 2
    DETERMINING_LOCATION = 3
    NAVIGATING_TO_START = 4
    SEARCH_MESSAGE = 5
    PICK_UP = 6

    def __int__(self):
        return self.value
