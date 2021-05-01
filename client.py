import socket
from netifaces import interfaces, ifaddresses, AF_INET
from time import time

working = True

def is_stopped():
    global working
    return not working

def stop():
    global working
    working = False

def ip4_addresses():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface)[AF_INET]:
            ip_list.append(link['broadcast'])
    return ip_list


def find_servers(on_find):

    broadcast = ([ip for ip in ip4_addresses() if ip.startswith("192.168")][0], 5555)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    while True:
        servers = {}
        if not working:
            return
        sock.sendto(b"memes", broadcast)
        sock.settimeout(2)
        t = time()
        while t + 3 > time():
            if not working:
                return
            try:
                name, addr = sock.recvfrom(1024)
                name = name.decode("utf8")
                if name in servers:
                    continue

                servers[name] = addr
                on_find(name, addr)
            except socket.timeout:
                pass



def connect(name, server):
    print("connecting to " + server[0])
    sock = socket.socket()
    sock.connect((server[0], server[1]))

    print("connected")
    sock.send(bytes(name, 'utf8'))
    return sock
