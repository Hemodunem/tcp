import socket

def connect(name):
    sock = socket.socket()
    sock.connect(('192.168.20.71', 5555))
    sock.send(bytes(name, 'utf8'))
    return sock

