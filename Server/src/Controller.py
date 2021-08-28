import socket

import Model
import ccard
import random
import jwt
import string
from Server import ClientSocket

secret = "".join(random.sample((string.ascii_letters + string.digits + string.punctuation), 64))


def handle_client(client_socket: ClientSocket) -> None:
    try:
        client_socket.conn.settimeout(60)
        packet_lengths = {"REGISTER": 4, "AUTHENTICATE": 3, "BALANCE": 2, "DEPOSIT": 3, "WITHDRAW": 3}
        routes = {"REGISTER": register, "AUTHENTICATE": authenticate, "BALANCE": balance, "DEPOSIT": deposit,
                  "WITHDRAW": withdraw}
        response = error("Invalid request.")
        packet = client_socket.receive_packet().strip().split("\t")
        if (len(packet) > 0) and (packet[0] in packet_lengths) and (packet_lengths[packet[0]] == len(packet)):
            response = routes[packet[0]](packet)
        client_socket.send_packet(response)
    except socket.timeout:
        client_socket.send_packet(error("Timeout error."))
    finally:
        client_socket.shutdown()
        client_socket.close()


def register(packet: list[str]) -> str:
    try:
        ssn, first_name, last_name = packet[1], packet[2], packet[3]
        account = str(ccard.visa())
        pin = str(random.randint(1111, 9999))
        Model.register(ssn, first_name, last_name, account, pin)
        return f"REGISTER\t{account},{pin}"
    except (Model.InvalidParameterError, Model.UserExistsError) as e:
        return error(e.message)
    except Model.AccountExistsError:
        return register(packet)


def authenticate(packet: list[str]) -> str:
    try:
        account, pin = packet[1], packet[2]
        if Model.getPin(account) == pin:
            return f"AUTHENTICATE\t{jwt.encode({'account': account}, secret, algorithm='HS256')}"
        return error("Authentication Failed.")
    except (Model.AccountNotFoundError, Model.InvalidParameterError):
        return error("Authentication Failed.")


def balance(packet: list[str]) -> str:
    try:
        account = decode(packet[1])
        if account is None: return error("Invalid token.")
        return f"BALANCE\t{Model.getBalance(account)['current']}"
    except (Model.InvalidParameterError, Model.AccountNotFoundError) as e:
        return error(e.message)


def deposit(packet: list[str]) -> str:
    try:
        account, amount = decode(packet[1]), float(packet[2])
        if account is None: return error("Invalid token.")
        deposit_summary = Model.deposit(account, amount)
        return f"DEPOSIT\t{deposit_summary['previous']}\t{deposit_summary['current']}"
    except (Model.InvalidParameterError, Model.AccountNotFoundError) as e:
        return error(e.message)
    except ValueError:
        return error("Invalid amount specified.")


def withdraw(packet: list[str]) -> str:
    try:
        account, amount = decode(packet[1]), float(packet[2])
        if account is None: return error("Invalid token.")
        withdraw_summary = Model.withdraw(account, amount)
        return f"WITHDRAW\t{withdraw_summary['previous']}\t{withdraw_summary['current']}"
    except (Model.InvalidParameterError, Model.AccountNotFoundError, Model.OverdraftError) as e:
        return error(e.message)
    except ValueError:
        return error("Invalid amount specified.")


def decode(token: str) -> str or None:
    try:
        decoded_token = jwt.decode(token, secret, algorithms='HS256')
        return str(decoded_token['account'])
    except jwt.exceptions.InvalidTokenError:
        return None


def error(msg: str) -> str:
    return f"ERROR\t{msg}"
