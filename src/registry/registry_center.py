#!/usr/bin/python3.5
from registry_router import RegistryRouter
from registry_handler import RemoteServiceHandler

import sys
sys.path.append('..')

from rpc_core.transport.rpc_acceptor import Bio_Acceptor

from rpc_core.codec.rpc_decoder import JSON_Decoder
from rpc_core.codec.rpc_encoder import JSON_Encoder

class MethodMetadata(object):

    def __init__(self, method_name, method_args, return_type):
        self.method_name = method_name
        self.method_args = method_args
        self.return_type = return_type

    @property
    def method_signature(self):
        return self.method_signature

    @method_signature.setter
    def method_signature(self, method_signature):
        self.method_signature = method_signature

class ServiceMetadata(object):

    def __init__(self, service_ip, service_port):
        self.service_ip = service_ip
        self.service_port = service_port
        self.method_list = []

    @property
    def service_name(self):
        return self.service_name  

    @service_name.setter
    def service_name(self, service_name):
        self.service_name = service_name

    def append_method(self, method_metadata):
        self.method_list.append(method_metadata)

class ServiceRepository:

    def __init__(self):
        self.registered_services = {}

    def add(self):
        pass

    def remove(self):
        pass

    def lookup(self, service_name, method_signature):
        services = self.registered_services.get(service_name)
        if not service_name:
            raise RuntimeError('No service instance - %s registered' % service_name)
        elif isinstance(services, list):
            if len(services) > 1:
                # TODO load-balance strategy should be implemented
                pass
            else:
                service = services[0]
                assert isinstance(service, ServiceMetadata)
                methods = service.method_list
                if not methods:
                    raise RuntimeError('No method registered for this service - %s.'\
                        % service_name)
                assert isinstance(methods, list)
                method_name = ''
                for method in methods:
                    assert isinstance(method, MethodMetadata)
                    if method.method_signature == method_signature:
                        method_name = method.method_name
                        break
                service_url = 'tcp://%s:%d/%s' % (service.service_ip, service.service_port, method_name)
                return service_url
        else:
            raise RuntimeError('Oops! An error occured in service registry!')

service_repo = ServiceRepository()

class RegistryCenter(object):
    '''
    All services registered in registry center should be like:
    {
        "accout_service" : {
            "deposit" : ["tcp://192.168.0.1:8888", "tcp://192.168.0.2:7777"],
            "withdraw" : ["tcp://192.168.0.3:7666", "amqp://192.168.0.4:9090"]
        },
        "user_service" : {
            "register" : ["http://192.168.0.5:8080"],
            "unregister" : []
        }
    }
    '''

    def __init__(self, tcp_port):
        RegistryRouter.init_routers()
        self.acceptor = Bio_Acceptor(tcp_port)
        self.acceptor.set_defaults()
        self.acceptor.dispatch_router = RemoteServiceHandler.handle_request_data

    def serve_forever(self):
        self.acceptor.serve_forever()


def main():
    registry_center = RegistryCenter(9999)
    import time
    time.sleep(2)
    registry_center.serve_forever()

if __name__=='__main__':
    main()
