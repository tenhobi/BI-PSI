import threading

from src.controller import Controller

from src.constants import RECV_SIZE


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
            try:
                data = self.socket.recv(RECV_SIZE)
                if data:
                    buffer = buffer + data
                    print(f'=== data {buffer}')
                    a = buffer.split(b'\a\b')
                    print(len(a))

                    if len(a) > 1:
                        print(f'zprava = {a[0]}')
                        buffer = buffer[len(a[0]) + 2:]
                        response, is_last = self.controller.process_message(a[0])
                        self.socket.send(response.encode())
                        print(f'sending ... f{response}')
                        if is_last:
                            break
                else:
                    raise Exception('Client disconnected')
            except Exception as e:
                print(e)
                self.socket.close()
                return False
