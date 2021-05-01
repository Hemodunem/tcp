import time
from base64 import b64encode
from os.path import getsize
from random import randint
from threading import Thread

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox, QFileDialog

from client import connect, find_servers, stop, is_stopped
from packet_manager import message_packet, file_packet, serialize, packet

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
        self.fileButton.clicked.connect(self.on_file_click)
        self.message.setFocusPolicy(Qt.StrongFocus)
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
            app.closeAllWindows()
            stop()

    def handle_chat(self):
        while True:
            if is_stopped():
                return
            try:
                data = self.sock.recv(1024)
                self.lines.append(data.decode("utf8"))
                self.show_lines()
            except:
                pass
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