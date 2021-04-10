from threading import Thread

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication

from client import connect

Form, Window = uic.loadUiType("chatWindow.ui")

class App(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(App, self).__init__()
        self.setupUi(self)
        self.send.clicked.connect(self.on_click)

        self.sock = connect()
        self.lines = []
        thread = Thread(target=self.handle_chat)
        thread.start()

    def handle_chat(self):
        while True:
            data = self.sock.recv(1024)
            self.lines.append(data.decode("utf8"))
            self.show_lines()

    def on_click(self):
        message = self.message.text()
        self.sock.send(bytes(message, 'utf8'))
        self.lines.append("Вы: " + message)
        self.show_lines()

    def show_lines(self):
        self.chat.clear()
        self.chat.addItems(self.lines)


app = QApplication([])
window = App()
window.show()
app.exec_()