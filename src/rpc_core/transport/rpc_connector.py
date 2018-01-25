#! /usr/bin/python3.5
import socket

class Bio_Connector(object):

    def __init__(self, tcp_ip, tcp_port):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port

    def __enter__(self):
        self.sk = socket.socket()
        self.sk.connect((self.tcp_ip, self.tcp_port))

    def send_data(self, data):
        self.sk.sendall(data)
        accept_data = str(self.sk.recv(1024), encoding="utf8")
        print("".join(("接收内容：", accept_data)))

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.sk:
            self.sk.close()