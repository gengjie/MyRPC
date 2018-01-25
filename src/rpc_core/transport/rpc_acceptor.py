#! /usr/bin/python3.5
import socketserver

class Bio_Acceptor(object):

    BUFFER_SIZE = 1024

    class MyRequestHandler(socketserver.BaseRequestHandler):
        
        def handle(self):
            conn = self.request
            addr = self.client_address
            recv_part = conn.recv(Bio_Acceptor.BUFFER_SIZE)
            payload = recv_part
            while recv_part and recv_part[len(recv_part)-1] != '\n':
                payload += conn.recv(Bio_Acceptor.BUFFER_SIZE)
            print (payload)
            payload = self.server.connector.payload_decoder(payload)
            assert isinstance(payload, dict)
            payload['service_ip'] = addr
            send_payload = self.server.connector.dispatch_router(payload)
            send_payload = self.server.connector.payload_encoder(send_payload)
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

    def serve_forever(self):
        self.tcp_server = socketserver.ThreadingTCPServer(('localhost', self.port), \
            RequestHandlerClass=Bio_Acceptor.MyRequestHandler)
        self.tcp_server.connector = self
        self.tcp_server.serve_forever()

