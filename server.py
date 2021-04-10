import socket
from threading import Thread

sock = socket.socket()
sock.bind(('192.168.20.71', 5555))
clients = {}

print("Server started")


def handle_client(name, conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        print(name + ': ' + data.decode("utf8"))

        for client in clients.values():
            if client == conn:
                continue

            message = name + ': ' + data.decode("utf8")
            client.send(bytes(message, "utf8"))


while True:
    print("waiting for connections")
    sock.listen()
    conn, addr = sock.accept()

    name = conn.recv(1024).decode('utf8')

    clients[name] = conn

    print('connected:', addr)
    Thread(target=handle_client, args=[name, conn, addr]).start()

