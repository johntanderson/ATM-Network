import socket
import threading
from typing import Callable


class Connection:
    def __init__(self, conn: socket.socket, addr: str):
        self.conn = conn
        self.addr = addr

    def receive_packet(self) -> str:
        data = ""
        while 1:
            packet = self.conn.recv(1024)
            if packet == b"":
                break
            data += packet.decode("utf-8")
        return data

    def send_packet(self, packet: str):
        self.conn.sendall(packet.encode("utf-8"))
        self.conn.shutdown(socket.SHUT_WR)


class Server:
    def __init__(self, host: str, port: int, on_connect: Callable[[Connection], None]):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.handler = on_connect
        self.running = False

    def start(self):
        self.running = True
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        while self.running:
            try:
                conn, addr = self.socket.accept()
                thread = threading.Thread(target=self.handler, args=[Connection(conn, addr)])
                thread.start()
            except socket.timeout:
                print("CONNECTION ERROR - TIMEOUT")

    def stop(self):
        self.running = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
        self.socket.close()
