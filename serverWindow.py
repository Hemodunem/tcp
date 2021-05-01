import socket
import time
from threading import Thread

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.uic.properties import QtGui

from server import share_info, handle_client, add_client, get_clients

Form, Window = uic.loadUiType("serverWindow.ui")





class App(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(App, self).__init__()
        self.server = socket.socket()
        self.setupUi(self)
        self.serverButton.clicked.connect(self.start_server)

    def start_server(self):
        server_name = self.serverName.text()

        thread1 = Thread(target=share_info, args=[server_name])
        thread1.start()

        self.server.bind(("0.0.0.0", 5555))

        thread2 = Thread(target=self.handle_server)
        thread2.start()

        thread3 = Thread(target=self.tick_clients)
        thread3.start()

    def show_clients(self):
        self.clients.clear()
        self.clients.addItems(get_clients().keys())

    def tick_clients(self):
        while window.isVisible():
            self.show_clients()
            time.sleep(1)

    def handle_server(self):
        while True:
            self.server.listen()
            conn, address = self.server.accept()

            name = conn.recv(1024).decode("utf8")

            add_client(name, conn)

            print(f"[{name}]", "Connected!")
            Thread(target=handle_client, args=[name, conn]).start()


app = QApplication([])
window = App()
window.show()
app.exec_()
