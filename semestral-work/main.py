from src.tcp_server import TcpServer

HOST = '127.0.0.1'
PORT = 65432


def main():
    try:
        TcpServer(HOST, PORT).start()
    except KeyboardInterrupt:
        print("Exiting because of keyboard interrupt.")


if __name__ == '__main__':
    main()
