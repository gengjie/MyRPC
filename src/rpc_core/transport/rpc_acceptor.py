#! /usr/bin/python3.5
import SocketServer

class Bio_Acceptor(object):

    BUFFER_SIZE = 1024

    class MyRequestHandler(SocketServer.BaseRequestHandler):
        
        def handle(self):
            while True:
                conn = self.request
                addr = self.client_address
                while True:
                    recv_part = conn.recv(Bio_Acceptor.BUFFER_SIZE)
                    payload = recv_part
                    while recv_part and recv_part[len(recv_part)-1] != '\n':
                        payload += conn.recv(Bio_Acceptor.BUFFER_SIZE)
                    print (payload)
                    payload = Bio_Acceptor.payload_decoder(payload)
                    assert isinstance(payload, dict)
                    payload['service_ip'] = addr
                    send_payload = Bio_Acceptor.dispatch_router(payload)
                    send_payload = Bio_Acceptor.payload_encoder(send_payload)
                    conn.sendall(send_payload)
                conn.close()


    def __init__(self, port):
        self.tcp_server = SocketServer.ThreadingTCPServer(('localhost', port), \
            RequestHandlerClass=Bio_Acceptor.MyRequestHandler)

    @property
    def payload_decoder(self):
        return self.payload_decoder

    @payload_decoder.setter
    def payload_decoder(self, payload_decoder):
        self.payload_decoder = payload_decoder

    @property
    def payload_encoder(self):
        return self.payload_encoder

    @payload_encoder.setter
    def payload_encoder(self, payload_encoder):
        self.payload_encoder = payload_encoder

    @property
    def dispatch_router(self):
        return self.dispatch_router

    @dispatch_router.setter
    def dispatch_router(self, dispatch_router):
        self.dispatch_router = dispatch_router

    def serve_forever(self):
        self.tcp_server.serve_forever()

