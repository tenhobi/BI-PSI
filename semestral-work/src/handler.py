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
                    self.socket.send(response.encode())
                    print(f'SENDING = "{response.encode()}"')

                    if is_last:
                        flag = False
                        print('break 1')
                        break
            else:
                print('break 2')
                break

        print('Disconnecting.')
        self.socket.close()
