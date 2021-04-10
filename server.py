import socket
from threading import Thread
import PyQt5

sock = socket.socket()
sock.bind(('192.168.20.71', 5555))
clients = []

print("Server started")


def handle_client(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        print(addr[0] + ': ' + data.decode("utf8"))

        for client in clients:
            if client == conn:
                continue

            message = addr[0] + ': ' + data.decode("utf8")
            client.send(bytes(message, "utf8"))


while True:
    print("waiting for connections")
    sock.listen()
    conn, addr = sock.accept()
    clients.append(conn)

    print('connected:', addr)
    Thread(target=handle_client, args=[conn, addr]).start()

