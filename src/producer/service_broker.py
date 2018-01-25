#! /usr/bin/python
import threading
import inspect
<<<<<<< 962bde3943c8642592f16706455f7afd08a24ddc
=======
import sys
sys.path.append('..')

from rpc_core.codec.rpc_encoder import JSON_Encoder
from rpc_core.codec.rpc_decoder import JSON_Decoder
from rpc_core.transport.rpc_connector import Bio_Connector
>>>>>>> daily commit

class ServiceContainer:
    '''
    service_instances = {
        foo : {
            foo_instance : {
                foo_func : foo_func_ref
            }
        },
        bar : {
            bar_instance : {
                bar_func : bar_func_ref
            }
        }
    }
    '''

    def __init__(self):
        self.service_instances = {}
        self.lock = threading.Lock()
    
    def add_service(self, service_name, service_instance, func):
        # assert inspect.ismethod(func)
        self.lock.acquire()
        si = self.service_instances.get(service_name)
        if si is not None:
            if si == service_instance:
                si_members = si[service_instance]
                assert isinstance(si_members, dict)
                if si_members.has_key(func.__name__):
                    self.lock.release()
                    raise RuntimeError('duplicated function name - %s \
                            for service name - %s'\
                            % (func.__name__, service_name))
                else:
                    si_members[func.__name__] = func
            else:
                self.lock.release()
                raise RuntimeError('duplicated service name - %s' % service_name)
        else:
            self.service_instances[service_name] = {
                service_instance : {
                    func.__name__ : func
                }
            }
        self.lock.release()

    def del_service(self, service_name, func_name):
        self.lock.acquire()
        if self.service_instances.has_key(service_name):
            si_info = self.service_instances.get(service_name)
            assert isinstance(si_info, dict)
            si = si_info.keys()[0]
            si_members = si_info.get(si)
            assert isinstance(si_members, dict)
            if si_members.has_key(func_name):
                si_members.pop(func_name)
                if not si_members.items():
                    self.service_instances.pop(service_name)
            else:
                self.lock.release()
                raise RuntimeError('No method - %s found for service - %s' % \
                        (func_name, service_name))
        else:
            self.lock.release()
            raise RuntimeError('No service - %s published!' % service_name)
        self.lock.release()

    def lookup_serv(self, service_name, func_name):
        if self.service_instances.has_key(service_name):
            si_info = self.service_instances.get(service_name)
            assert isinstance(si_info, dict)
            for _, si_members in si_info:
                break
            assert isinstance(si_members, dict)
            callback = si_members.get(func_name)
            if not callback or not callable(callback):
                return callback
            raise TypeError
        else:
            raise RuntimeError('No service instance found for %s.' % service_name)

service_container = ServiceContainer()

class ServiceBroker:
    '''
    class HelloService:
        name = "hello_service"

        def say_hello(s):
            print s


    ServiceBroker Usage:

    service_broker = ServiceBroker("tcp://localhost:6666", 7777)
    service_broker.publish(HelloService, HelloService.say_hello)

    - registry_url = tcp://localhost:6666
    - broker_port = broker_port

    '''

    def __init__(self, registry_url, broker_port):
        self.registry_url = registry_url
        self.broker_port = broker_port

    def publish(self, service_cls, method):
        assert inspect.isclass(service_cls)
        service_name = service_cls.__dict__.get('name')
        service_instance = service_cls()
        service_container.add_service(service_name, service_instance, method)
        self.__register(service_name, method.__name__)

    def __register(self, service_name, method_name):
        registry_info = self.registry_url.split("://")
        proto = registry_info[0]
        registry_ip, registry_port = registry_info[1].split(":")
        if proto == 'tcp':
            with Bio_Connector(registry_ip, registry_port) as connector:
                data = {
                    "header" : {
                        "routing_key" : "api/service/register",
                        "request_method" : "POST"
                    },
                    "body" : {
                        "service_port" : self.broker_port,
                        "service_name" : service_name,
                        "method_name" : method_name
                    }
                }
                connector.send_data(JSON_Encoder, data)
                rst = connector.recv_data(JSON_Decoder)
                print (rst)
        else:
            raise "Not supported!"


class HelloService:
    name = "hello_service"

    def say_hello(self, _s):
        print (_s)


if __name__ == '__main__':
    service_broker = ServiceBroker("tcp://localhost:9999", 7777)
    service_broker.publish(HelloService, HelloService.say_hello)
