import socket
from threading import Thread

server_name = input("Name: ")


def share_info():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind(("0.0.0.0", 5555))
    print("Server started")

    while True:
        m, addr = sock.recvfrom(4096)
        sock.sendto(bytes(server_name, "utf8"), addr)


thread = Thread(target=share_info)
thread.start()


def handle_client(client_name, client_sock):
    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break

            print(client_name + ': ' + data.decode("utf8"))

            for client in clients.values():
                if client == client_sock:
                    continue

                message = client_name + ': ' + data.decode("utf8")
                client.send(bytes(message, "utf8"))
    except socket.error:
        print(client_name, "disconnected")


server = socket.socket()
server.bind(('0.0.0.0', 5555))
clients = {}

while True:
    server.listen()
    conn, address = server.accept()

    name = conn.recv(1024).decode('utf8')

    clients[name] = conn

    print(name, "connected")
    Thread(target=handle_client, args=[name, conn, address]).start()