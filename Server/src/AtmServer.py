import socket
import threading
from ClientThread import handle_client, Connection


class Server:
    def __init__(self, host: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.running = False

    def start(self):
        self.running = True
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f"Server is listening on {self.host}:{self.port}...")
        while self.running:
            try:
                conn, addr = self.socket.accept()
                thread = threading.Thread(target=handle_client, args=[Connection(conn, addr)])
                thread.start()
            except socket.timeout:
                print("CONNECTION ERROR - TIMEOUT")

    def stop(self):
        self.running = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
        self.socket.close()
