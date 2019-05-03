from enum import Enum

from src.robot import Robot
from src.constants import KEY_SERVER, KEY_CLIENT


class Controller(object):
    def __init__(self):
        # Server messages.
        self.SERVER_MOVE = "102 MOVE\a\b"
        self.SERVER_TURN_LEFT = "103 TURN LEFT\a\b"
        self.SERVER_TURN_RIGHT = "104 TURN RIGHT\a\b"
        self.SERVER_PICK_UP = "105 GET MESSAGE\a\b"
        self.SERVER_LOGOUT = "106 LOGOUT\a\b"
        self.SERVER_OK = "200 OK\a\b"
        self.SERVER_LOGIN_FAILED = "300 LOGIN FAILED\a\b"
        self.SERVER_SYNTAX_ERROR = "301 SYNTAX ERROR\a\b"
        self.SERVER_LOGIC_ERROR = "302 LOGIC ERROR\a\b"

        # Client messages.
        self.CLIENT_FULL_POWER = "FULL POWER"
        self.CLIENT_RECHARGING = "RECHARGING"

        # Client messages' limits.
        self.CLIENT_USERNAME_LENGTH = 10
        self.CLIENT_CONFIRMATION_LENGTH = 5
        self.CLIENT_OK_LENGTH = 10
        self.CLIENT_MESSAGE_LENGTH = 98

        # Timeouts.
        self.TIMEOUT = 1
        self.TIMEOUT_CHARGING = 5

        # Keys.
        self.KEY_SERVER = KEY_SERVER
        self.KEY_CLIENT = KEY_CLIENT

        # Data.
        self.robot = None
        self.state = State.USER_NAME
        self.charging = False

    def process_message(self, message):
        if self.state == State.USER_NAME:
            self.robot = Robot(message)
            self.state = State.CONFIRMATION

            if self.robot.serverHash == 0:
                return self.SERVER_SYNTAX_ERROR, True

            return f'{self.robot.serverHash}\a\b', False

        return self.SERVER_SYNTAX_ERROR, True


class State(Enum):
    USER_NAME = 1
    CONFIRMATION = 2
    FIRST_MOVE = 3
    SECOND_MOVE = 4
    NAVIGATING_TO_ZONE = 5
    SEARCH_ZONE = 6
    PICK_UP = 7
