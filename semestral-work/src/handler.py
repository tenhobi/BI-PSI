import re
import socket
import threading

from src.constants import Constants
from src.controller import Controller


class Handler(threading.Thread):
    def __init__(self, address, socket):
        super().__init__()
        self.address = address
        self.socket = socket
        self.controller = Controller()

    def run(self):
        print(f'Connected to {self.address}')

        buffer = b''
        flag = True

        while flag:
            try:
                data = self.socket.recv(Constants.RECV_SIZE)
            except socket.timeout:
                print('TIMEOUT')
                print('break 4')
                break

            if data:
                buffer += data

                # Split buffer to messages, removing the trail empty.
                for match in re.finditer(b'(.*?)(?:\a\b)', buffer):
                    self.socket.settimeout(self.controller.get_timeout())
                    message = match.group(1).decode("utf-8")
                    print(f'--- MESSAGE = "{match.group(1)}"', buffer, message)

                    # Remove the message from buffer (including \a\b).
                    buffer = buffer[len(message) + 2:]

                    response, is_last = self.controller.process(message)

                    print('DONE')

                    if response == Constants.SERVER_INTERNAL_RECHARGING:
                        print('xxx recharging')
                        self.socket.settimeout(self.controller.get_timeout())
                        continue
                    elif response == Constants.SERVER_INTERNAL_FULL_POWER:
                        print('xxx full')
                        continue

                    self.socket.send(response.encode())
                    print(f'SENDING = "{response.encode()}"')

                    if is_last:
                        flag = False
                        print('break 1')
                        break
                else:
                    if buffer[-1:] == b'\a':
                        print('AAAAA', self.controller.state, buffer)
                        if self.controller.is_message_long(buffer[:-1].decode("utf-8")):
                            message = buffer[:-1].decode('utf-8')
                            if message == Constants.CLIENT_RECHARGING or message == Constants.CLIENT_FULL_POWER:
                                continue

                            print('break 5')
                            self.socket.send(Constants.SERVER_SYNTAX_ERROR.encode())
                            flag = False
                            break
                    elif self.controller.is_message_long(buffer.decode("utf-8")):
                        message = buffer.decode('utf-8')
                        if message == Constants.CLIENT_RECHARGING or message == Constants.CLIENT_FULL_POWER:
                            continue

                        print('break 6')
                        self.socket.send(Constants.SERVER_SYNTAX_ERROR.encode())
                        flag = False
                        break
            else:
                print('break 2')
                break

        print('Disconnecting.')
        self.socket.close()
