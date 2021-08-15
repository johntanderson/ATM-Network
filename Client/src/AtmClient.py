import socket


class Client:
    def __init__(self, host: str, port: int):
        self.token = None
        self.socket = None
        self.host = host
        self.port = port
        self.format = 'utf-8'

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def send_packet(self, packet):
        self.socket.sendall(packet.encode(self.format))
        self.socket.shutdown(socket.SHUT_WR)

    def receive_packet(self) -> list[str]:
        data = ""
        while 1:
            packet = self.socket.recv(1024)
            if packet == b"":
                break
            data += packet.decode("utf-8")
        return data.strip().split('\t')

    def register(self, ssn: str, first_name: str, last_name: str) -> list[str]:
        self.connect()
        self.send_packet(f"REGISTER\t{ssn}\t{first_name}\t{last_name}")
        res = self.receive_packet()
        self.disconnect()
        return res

    def authenticate(self, account_number, pin):
        self.connect()
        self.send_packet(f"AUTHENTICATE\t{account_number},{pin}")
        res = self.receive_packet()
        self.disconnect()
        return res

    def balance(self):
        self.connect()
        self.send_packet(f"BALANCE\t{self.token}")
        res = self.receive_packet()
        self.disconnect()
        return res

    def deposit(self, amount):
        self.connect()
        self.send_packet(f"DEPOSIT\t{self.token}\t{amount}")
        res = self.receive_packet()
        self.disconnect()
        return res

    def withdraw(self, amount):
        self.connect()
        self.send_packet(f"WITHDRAW\t{self.token}\t{amount}")
        res = self.receive_packet()
        self.disconnect()
        return res
