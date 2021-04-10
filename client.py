import socket

def connect():
    sock = socket.socket()
    sock.connect(('192.168.20.71', 5555))
    return sock

