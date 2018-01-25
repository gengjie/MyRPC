#! /usr/bin/python3.5
import socketserver

from rpc_core.codec.rpc_decoder import JSON_Decoder
from rpc_core.codec.rpc_encoder import JSON_Encoder

class Bio_Acceptor(object):
    "https://docs.python.org/2/library/socketserver.html"

    BUFFER_SIZE = 1024

    class MyRequestHandler(socketserver.StreamRequestHandler):
        
        def handle(self):
            conn = self.request
            payload = self.rfile.readline().strip()
            payload = self.server.connector.payload_decoder.decode(payload)
            payload['body']['service_ip'] = self.client_address[0]
            send_payload = self.server.connector.dispatch_router(payload)
            send_payload = self.server.connector.payload_encoder.encode_data(send_payload)
            conn.sendall(send_payload)
            conn.close()


    def __init__(self, port):
        self._dispatch_router = None
        self.port = port
        self.tcp_server = None
        self._payload_encoder = None
        self._payload_decoder = None

    @property
    def payload_decoder(self):
        return self._payload_decoder

    @payload_decoder.setter
    def payload_decoder(self, payload_decoder):
        self._payload_decoder = payload_decoder

    @property
    def payload_encoder(self):
        return self._payload_encoder

    @payload_encoder.setter
    def payload_encoder(self, payload_encoder):
        self._payload_encoder = payload_encoder

    @property
    def dispatch_router(self):
        return self._dispatch_router

    @dispatch_router.setter
    def dispatch_router(self, dispatch_router):
        self._dispatch_router = dispatch_router

    def set_defaults(self):
        self.payload_decoder = JSON_Decoder
        self.payload_encoder = JSON_Encoder

    def serve_forever(self):
        self.tcp_server = socketserver.ThreadingTCPServer(('localhost', self.port), \
            RequestHandlerClass=Bio_Acceptor.MyRequestHandler)
        self.tcp_server.connector = self
        self.tcp_server.serve_forever()

