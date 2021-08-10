import socket

HOST = "0.0.0.0"
PORT = 56789
FORMAT = 'utf-8'


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    send_packet(client, "TEST\tTEST\tTEST\t1\t2\t3")
    res = recv_packet(client)
    client.close()
    print(res)


def recv_packet(conn: socket.socket) -> str:
    data = ""
    while 1:
        packet = conn.recv(1024)
        if packet == b"":
            break
        data += packet.decode(FORMAT)
    return data


def send_packet(conn: socket.socket, message: str):
    conn.sendall(message.encode(FORMAT))
    conn.shutdown(socket.SHUT_WR)


main()
