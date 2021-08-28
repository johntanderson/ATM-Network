import socket
import threading
from typing import Callable


class ClientSocket:
    def __init__(self, conn: socket.socket, address: str):
        self.conn = conn
        self.address = address
        print(f"CONNECTION ESTABLISHED:\t{address}")

    def receive_packet(self) -> str:
        data = ""
        while 1:
            packet = self.conn.recv(1024)
            if packet == b"":
                break
            data += packet.decode("utf-8")
        print(f"REQUEST:\t{self.address} - {data}")
        return data

    def send_packet(self, packet: str):
        print(f"RESPONSE:\t{self.address} - {packet}")
        self.conn.sendall(packet.encode("utf-8"))

    def close(self):
        self.conn.close()
        print(f"CONNECTION CLOSED:\t{self.address}")

    def shutdown(self):
        self.conn.shutdown(socket.SHUT_WR)


class Server:
    def __init__(self, host: str, port: int, handler: Callable[[ClientSocket], None]):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.handle = handler
        self.running = False

    def start(self):
        self.running = True
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f"Server is listening on {self.host}:{self.port}...")
        while self.running:
            try:
                conn, address = self.socket.accept()
                thread = threading.Thread(target=self.handle, args=[ClientSocket(conn, address)])
                thread.start()
            except socket.timeout:
                print("CONNECTION ERROR - TIMEOUT")

    def stop(self):
        self.running = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
        self.socket.close()
