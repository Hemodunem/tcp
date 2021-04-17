from threading import Thread

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox

from client import connect, find_servers

currentServer = ('0.0.0.0', 5555)

Form, Window = uic.loadUiType("chatWindow.ui")
Form1, Window1 = uic.loadUiType('connectWindow.ui')


class ServersWindow(QtWidgets.QMainWindow, Form1):
    def on_find_server(self, name, addr):
        self.servers[name] = addr
        self.show_servers()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectButton.clicked.connect(self.on_click)
        self.servers = {}

        Thread(target=find_servers, args=[self.on_find_server]).start()

    def on_click(self):
        global currentServer
        items = self.serversView.selectedItems()
        if len(items) < 1:
            return

        name = items[0].text()
        currentServer = self.servers[name]

        main_window.show()
        main_window.get_name()

    def show_servers(self):
        self.serversView.clear()
        self.serversView.addItems(self.servers.keys())


class App(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(App, self).__init__()
        self.setupUi(self)
        self.send.clicked.connect(self.on_click)
        self.message.returnPressed.connect(self.on_click)
        self.sock = None
        self.lines = []

    def get_name(self):
        global currentServer
        name, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        if ok:
            self.sock = connect(name, currentServer)

            thread = Thread(target=self.handle_chat)
            thread.start()
        else:
            box = QMessageBox()
            box.setText('Ухади')
            box.exec()
            quit()

    def handle_chat(self):
        while True:
            data = self.sock.recv(1024)
            self.lines.append(data.decode("utf8"))
            self.show_lines()

    def on_click(self):
        message = self.message.text()
        message = message.strip(' ')
        if message == '':
            pass
        else:
            self.sock.send(bytes(message, 'utf8'))
            self.lines.append("Вы: " + message)
            self.show_lines()
            self.message.setText('')

    def show_lines(self):
        self.chat.clear()
        self.chat.addItems(self.lines)

    def closeEvent(self, event):
        quit()



app = QApplication([])
window = ServersWindow()
window.show()

main_window = App()
app.exec_()
