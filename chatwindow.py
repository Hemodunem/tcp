import time
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox, QFileDialog
from base64 import b64encode
from os.path import getsize
from random import randint
from threading import Thread

from client import connect, find_servers, stop, is_stopped
from packet_manager import message_packet, file_packet, serialize, packet, unserialize

currentServer = ('0.0.0.0', 5555)

Form, Window = uic.loadUiType("chatWindow.ui")
Form1, Window1 = uic.loadUiType('connectWindow.ui')


class ServersWindow(QtWidgets.QMainWindow, Form1):
    def closeEvent(self, event):
        app.closeAllWindows()
        stop()
        print('sds')

    def on_find_server(self, name, addr):
        self.servers[name] = addr
        self.show_servers()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectButton.clicked.connect(self.on_click)
        self.servers = {}

        thread = Thread(target=find_servers, args=[self.on_find_server])
        thread.start()

    def on_click(self):
        global currentServer
        items = self.serversView.selectedItems()
        if len(items) < 1:
            addr = self.ipLine.text().split(':')
            currentServer = (addr[0], int(addr[1]))
        else:
            name = items[0].text()
            currentServer = self.servers[name]
        if currentServer is None:
            return

        main_window.show()
        main_window.get_name()

    def show_servers(self):
        print("show servers")
        last = [str(self.serversView.item(i).text()) for i in range(self.serversView.count())]

        items_to_add = [server for server in self.servers.keys() if server not in last]
        items_to_remove = [name for name in last if name not in self.servers.keys()]

        for name in items_to_add:
            self.serversView.addItem(name)

        for name in items_to_remove:
            print("remove " + name)
            item = self.serversView.findItems(name, Qt.MatchExactly)
            row = self.serversView.row(item)
            self.serversView.takeItem(row)


class App(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(App, self).__init__()
        self.setupUi(self)
        self.send.clicked.connect(self.on_click)
        self.fileButton.clicked.connect(self.on_file_click)
        self.message.setFocusPolicy(Qt.StrongFocus)
        self.message.returnPressed.connect(self.on_click)
        self.sock = None
        self.name = ""
        self.lines = []

    def get_name(self):
        global currentServer
        name, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        if ok:
            if name == '':
                self.get_name()
            else:
                self.name = name
                self.sock = connect(self.name, currentServer)

                thread = Thread(target=self.handle_chat)
                thread.start()
        else:
            box = QMessageBox()
            box.setText('Ухади')
            box.exec()
            app.closeAllWindows()
            stop()

    def handle_chat(self):
        while True:
            if is_stopped():
                return
            try:
                data = self.sock.recv(1024)

                try:
                    packet = unserialize(data)
                    packet_type = packet["type"]
                    payload = packet["payload"]

                    if packet_type == "message":
                        if payload["sender"] == self.name:
                            return

                        self.lines.append(payload["sender"] + ": " + payload["text"])
                        self.show_lines()
                except:
                    print("error")


            except:
                print("error")

    def on_file_click(self):
        filename, filetype = QFileDialog.getOpenFileName(self,
                                                         "Выбрать файл",
                                                         ".",
                                                         "All Files(*)")
        print(filename)

        file_id = str(randint(0, 9999999))
        self.sock.sendall(serialize(
            packet("file", {
                "file_id": file_id,
                "size": getsize(filename)
            })
        ))

        with open(filename, mode='rb') as file:  # b is important -> binary
            aee = 0
            while True:
                bytes_read = file.read(1024)
                if not bytes_read:
                    break
                self.sock.sendall(bytes_read)
                aee += len(bytes_read)

        print(str(aee))

    def on_click(self):
        message = self.message.text()
        message = message.strip(' ')
        self.message.setFocus()

        if message == '':
            pass
        else:
            self.sock.send(message_packet(message))
            self.lines.append("Вы: " + message)
            self.show_lines()
            self.message.setText('')

    def show_lines(self):
        self.chat.clear()
        self.chat.addItems(self.lines)

    def closeEvent(self, event):
        app.closeAllWindows()
        stop()
        self.sock.close()


app = QApplication([])
window = ServersWindow()
window.show()

main_window = App()
app.exec_()
