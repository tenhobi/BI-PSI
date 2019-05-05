import socket

from src.handler import Handler


class TcpServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def start(self):
        print(f'Listening on {(self.host, self.port)}')

        self.socket.listen(5)
        while True:
            self.socket.setblocking(True)
            client, address = self.socket.accept()
            self.socket.setblocking(False)
            thread = Handler(address, client)
            thread.start()
