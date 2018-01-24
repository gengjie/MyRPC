#!/usr/bin/python3.5
from registry_router import RegistryRouter

import sys
sys.path.append('..')

from rpc_core.transport.rpc_acceptor import Bio_Acceptor

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


class RegistryCenter(object):

    def __init__(self, tcp_port):
        self.registered_services = {}
        RegistryRouter.init_routers()
        self.acceptor = Bio_Acceptor(tcp_port)
        self.acceptor.dispatch_router = RegistryRouter.dispatch

    def serve_forever(self):
        self.acceptor.serve_forever()

    def register_service(self):
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


def main():
    print("dfsdfasdfasdf")
    registry_center = RegistryCenter(9999)
    import time
    time.sleep(2)
    registry_center.serve_forever()

if __name__=='__main__':
    main()
