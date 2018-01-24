#! /usr/bin/python3.5
import socket

class Bio_Connector(object):

    def __init__(self, tcp_ip, tcp_port):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.sk = socket.socket()

    def esteblish_connection(self):
        self.sk.connect((self.tcp_ip, self.tcp_port))

    def send_data(self, data):
        while True:
            send_data = input("输入发送内容:")
            self.sk.sendall(bytes(send_data, encoding="utf8"))
            if send_data == "byebye":
                break
            accept_data = str(self.sk.recv(1024), encoding="utf8")
            print("".join(("接收内容：", accept_data)))

    def destory(self):
        if self.sk:
            self.sk.close()