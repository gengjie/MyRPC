#!/usr/bin/python3.5
from registry_router import RegistryRouter
from registry_handler import RemoteServiceHandler

import threading
import sys
sys.path.append('..')

from rpc_core.transport.rpc_acceptor import Bio_Acceptor

from rpc_core.codec.rpc_decoder import JSON_Decoder
from rpc_core.codec.rpc_encoder import JSON_Encoder

from rpc_core.exceptions import ExistedMethod
from rpc_core.exceptions import NotExistedService
from rpc_core.exceptions import NotExistedMethod
from rpc_core.exceptions import ServiceRegistryException

class ServiceRepository:
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

    def __init__(self):
        self.lock = threading.Lock()
        self.registered_services = {}

    def add(self, service_name, method_name, service_uri):
        self.lock.acquire()
        if service_name in self.registered_services:
            service_info = self.registered_services.get(service_name)
            assert isinstance(service_info, dict)
            if method_name in service_info:
                service_uri_list = service_info.get(method_name)
                assert isinstance(service_uri_list, list)
                if service_uri not in service_uri_list:
                    service_uri_list.append(service_uri)
                else:
                    self.lock.release()
                    raise ExistedMethod(method_name)
            else:
                service_info[method_name] = [service_uri]
        else:
            self.registered_services[service_name] = {
                method_name : [service_uri]
            }
        self.lock.release()

    def remove(self, service_name, method_name, service_uri):
        self.lock.acquire()
        if service_name in self.registered_services:
            service_info = self.registered_services.get(service_name)
            assert isinstance(service_info, dict)
            if method_name in service_info:
                service_uri_list = service_info.get(method_name)
                assert isinstance(service_uri_list, list)
                if service_uri not in service_uri_list:
                    self.lock.release()
                    raise ServiceRegistryException()
                else:
                    service_uri_list.remove('%s/%s/%s' % (service_uri, \
                        service_name, method_name))
            else:
                self.lock.release()
                raise NotExistedMethod(service_name, method_name)
        else:
            self.lock.release()
            raise NotExistedService(service_name)
        self.lock.release()

    def lookup(self, service_name, method_name):
        service_info = self.registered_services.get(service_name)
        if not service_info:
            raise NotExistedService(service_name)
        method_info = service_info.get(method_name)
        if not method_info:
            raise ServiceRegistryException()
        else:
            if len(method_info) > 1:
                # TODO load-balance strategy should be implemented
                pass
            else:
                service_uri = method_info[0]
                return service_uri

service_repo = ServiceRepository()

class RegistryCenter(object):

    def __init__(self, tcp_port):
        RegistryRouter.init_routers()
        self.acceptor = Bio_Acceptor(tcp_port)
        self.tcp_port = tcp_port
        self.acceptor.set_defaults()
        self.acceptor.request_handler = RemoteServiceHandler.handle_request_data

    def serve_forever(self):
        ''' used to start service for registry center '''
        print ("service registry is booting and listening port %d..." % int(self.tcp_port))
        self.acceptor.serve_forever()


def main():
    registry_center = RegistryCenter(9999)
    registry_center.serve_forever()

if __name__=='__main__':
    main()
