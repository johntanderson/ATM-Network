from AtmServer import *
import sys


def main():
    server.start()


def handle_client(connection: Connection):
    packet = connection.receive_packet()
    print(f"{connection.addr} - {packet}")
    connection.send_packet("OK")


server = Server(host="0.0.0.0", port=56789, on_connect=handle_client)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Cleaning up...")
        server.stop()
        sys.exit(0)
