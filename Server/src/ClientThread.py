import socket
import ccard
import random
import jwt
import AtmDatabase
import string


secret = "".join(random.sample((string.ascii_letters + string.digits + string.punctuation), 64))


class Connection:
    def __init__(self, conn: socket.socket, addr: str):
        self.conn = conn
        self.addr = addr

    def receive_packet(self) -> list[str]:
        data = ""
        while 1:
            packet = self.conn.recv(1024)
            if packet == b"":
                break
            data += packet.decode("utf-8")
        return data.strip().split('\t')

    def send_packet(self, packet: str):
        self.conn.sendall(packet.encode("utf-8"))
        self.conn.shutdown(socket.SHUT_WR)


def handle_client(connection: Connection):
    packet = connection.receive_packet()
    print(f"{connection.addr} - {packet}")
    if packet is None:
        connection.send_packet(error("Unknown Request"))
        return
    if packet[0] == "REGISTER" and len(packet) == 4:
        connection.send_packet(register(packet))
        return
    if packet[0] == "AUTHENTICATE" and len(packet) == 2:
        connection.send_packet(authenticate(packet))
        return
    if packet[0] == "BALANCE" and len(packet) == 2:
        connection.send_packet(balance(packet))
        return
    if packet[0] == "DEPOSIT" and len(packet) == 3:
        connection.send_packet(deposit(packet))
        return
    if packet[0] == "WITHDRAW":
        connection.send_packet(withdraw(packet))
        return
    connection.send_packet(error("Unknown Request"))


def register(packet) -> str:
    account = ccard.visa()
    pin = str(random.randint(1111, 9999))
    if AtmDatabase.register(ssn=packet[1], first_name=packet[2], last_name=packet[3], account_num=account, pin=pin):
        return f"REGISTER\t{account},{pin}"
    return error("Registration Error")


def authenticate(packet) -> str:
    account_details = packet[1].split(',')
    if AtmDatabase.authenticate(account_num=account_details[0], pin=account_details[1]):
        return f"AUTHENTICATE\t{jwt.encode({'account_number': account_details[0]}, secret, algorithm='HS256')}"
    return error("Authentication Error")


def balance(packet) -> str:
    try:
        decoded_token = jwt.decode(packet[1], secret, algorithms='HS256')
        account = str(decoded_token['account_number'])
        return f"BALANCE\t{AtmDatabase.balance(account_num=account)}"
    except Exception as e:
        print(e)
        return error("Authentication Error")


def deposit(packet) -> str:
    try:
        decoded_token = jwt.decode(packet[1], secret, algorithms='HS256')
        account = str(decoded_token['account_number'])
        prev_balance = AtmDatabase.balance(account_num=account)
        AtmDatabase.deposit(account_num=account, amount=float(packet[2]))
        new_balance = AtmDatabase.balance(account_num=account)
        return f"DEPOSIT\t{prev_balance},{new_balance}"
    except Exception as e:
        print(e)
        return error("Authentication Error")


def withdraw(packet) -> str:
    try:
        decoded_token = jwt.decode(packet[1], secret, algorithms='HS256')
        account = str(decoded_token['account_number'])
        prev_balance = AtmDatabase.balance(account_num=account)
        AtmDatabase.withdraw(account_num=account, amount=float(packet[2]))
        new_balance = AtmDatabase.balance(account_num=account)
        return f"WITHDRAW\t{prev_balance},{new_balance}"
    except Exception as e:
        print(e)
        return error("Authentication Error")


def error(msg: str) -> str:
    return f"ERROR\t{msg}"
