class Constants(object):
    RECV_SIZE = 1024

    # Keys.
    KEY_SERVER = 54621
    KEY_CLIENT = 45328

    # Client messages.
    CLIENT_FULL_POWER = 'FULL POWER'
    CLIENT_RECHARGING = 'RECHARGING'

    # Client messages' limits.
    CLIENT_USERNAME_LENGTH = 12 - 2
    CLIENT_CONFIRMATION_LENGTH = 7 - 2
    CLIENT_OK_LENGTH = 12 - 2
    CLIENT_MESSAGE_LENGTH = 100 - 2

    # Timeouts.
    TIMEOUT = 1
    TIMEOUT_RECHARGING = 5

    # Server messages.
    SERVER_MOVE = '102 MOVE\a\b'
    SERVER_TURN_LEFT = '103 TURN LEFT\a\b'
    SERVER_TURN_RIGHT = '104 TURN RIGHT\a\b'
    SERVER_PICK_UP = '105 GET MESSAGE\a\b'
    SERVER_LOGOUT = '106 LOGOUT\a\b'
    SERVER_OK = '200 OK\a\b'
    SERVER_LOGIN_FAILED = '300 LOGIN FAILED\a\b'
    SERVER_SYNTAX_ERROR = '301 SYNTAX ERROR\a\b'
    SERVER_LOGIC_ERROR = '302 LOGIC ERROR\a\b'

    # Server internal messages.
    SERVER_INTERNAL_RECHARGING = '666 RECHARGING\a\b'
    SERVER_INTERNAL_FULL_POWER = '666 FULL POWER\a\b'
