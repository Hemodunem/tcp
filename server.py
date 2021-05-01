import socket
from threading import Thread

from packet_manager import unserialize, serialize

clients = {}
def get_clients():
    return clients


def add_client(name, client):
    clients[name] = client


def remove_client(name):
    clients.pop(name)


def handle_client(client_name, client_sock):
    try:
        files = []

        while True:
            data = client_sock.recv(1024)
            if not data:
                break

            try:
                packet = unserialize(data)
                packet_type = packet["type"]
                payload = packet["payload"]

                if packet_type == "message":
                    print(f"[{client_name}]: " + payload["text"])

                    send_all_except([client_sock], serialize(packet))
                elif packet_type == "file":
                    print(f"[{client_name}]: отправил файл (ID: {payload['file_id']})")

                    files.append(payload["file_id"])
                    left = payload["size"]
                    print(str(left))

                    while left > 0:
                        readed = min(left, 1024)
                        data = client_sock.recv(readed)
                        left -= readed
                        print("readed " + str(readed))

                    # send_all_except([client_sock], serialize(packet))

            except:
                print("[ERROR]", "Can't decode packet!")
                try:
                    print(f"[{client_name}]: " + data.decode("utf8"))
                except:
                    print(f"[{client_name}]: " + str(data))

    except socket.error:
        print(f"[{client_name}]", "Disconnected!")
        remove_client(client_name)


def send_all(packet):
    for client in get_clients().values():
        client.send(packet)


def send_all_except(exceptions, packet):
    for client in get_clients().values():
        if client in exceptions:
            continue

        client.send(packet)


def share_info(server_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind(("0.0.0.0", 5555))
    print("[SERVER]", "Started!")

    while True:
        m, addr = sock.recvfrom(4096)
        sock.sendto(bytes(server_name, "utf8"), addr)


if __name__ == "__main__":
    s_name = input("Name: ")

    thread = Thread(target=share_info, args=[s_name])
    thread.start()

    server = socket.socket()
    server.bind(("0.0.0.0", 5555))
    clients = {}

    while True:
        server.listen()
        conn, address = server.accept()

        name = conn.recv(1024).decode("utf8")

        add_client(name,conn)

        print(f"[{name}]", "Connected!")
        Thread(target=handle_client, args=[name, conn]).start()
