#! /usr/bin/python3.5
import socket

from rpc_core.codec.rpc_encoder import BaseEncoder
from rpc_core.codec.rpc_decoder import BaseDecoder

class Bio_Connector(object):

    def __init__(self, tcp_ip, tcp_port):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.sk = None

    def __enter__(self):
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sk.connect((self.tcp_ip, int(self.tcp_port)))
        return self

    def send_data(self, encoder, data):
        assert issubclass(encoder, BaseEncoder)
        self.sk.sendall(encoder.encode_data(data))

    def recv_data(self, decoder):
        rfile = self.sk.makefile(mode='r', buffering=1024, \
                encoding='utf8')
        accept_data = rfile.readline()
        assert issubclass(decoder, BaseDecoder)
        print ('ad', accept_data)
        return decoder.decode(accept_data)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.sk:
            self.sk.close()
