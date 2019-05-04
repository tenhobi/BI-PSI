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

        while True:
            self.socket.settimeout(self.controller.get_timeout())

            data = self.socket.recv(Constants.RECV_SIZE)
            if data:
                buffer = buffer + data
                messages = buffer.split(b'\a\b')

                if len(messages) > 1:
                    print(f'zprava = {messages[0]}')
                    buffer = buffer[len(messages[0]) + 2:]
                    print('alpha')
                    response, is_last = self.controller.process(messages[0].decode("utf-8"))
                    print('beta')
                    self.socket.send(response.encode())
                    print(f'sending ... f{response}')
                    if is_last:
                        break
            else:
                print('Client disconnected.')
                break

        self.socket.close()
