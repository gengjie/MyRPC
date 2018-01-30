#! /usr/bin/python
import threading
import inspect
from functools import wraps

import sys
sys.path.append('..')

from rpc_core.utils import make_request
from rpc_core.utils import get_host_ip
from rpc_core.utils import handle_result
from rpc_core.exceptions import IncorrectSignature
from rpc_core.codec.rpc_encoder import JSON_Encoder
from rpc_core.codec.rpc_decoder import JSON_Decoder
from rpc_core.transport.rpc_connector import Bio_Connector
from rpc_core.transport.rpc_acceptor import Bio_Acceptor

from rpc_core.exceptions import serialize
from rpc_core.exceptions import MethodNotFound

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
                if func.__name__ in si_members:
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
        if service_name in self.service_instances:
            si_info = self.service_instances.get(service_name)
            assert isinstance(si_info, dict)
            si = si_info.keys()[0]
            si_members = si_info.get(si)
            assert isinstance(si_members, dict)
            if func_name in si_members:
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
        if service_name in self.service_instances:
            si_info = self.service_instances.get(service_name)
            assert isinstance(si_info, dict)
            service_instance = None
            for service_instance, si_members in si_info.items():
                break
            assert isinstance(si_members, dict)
            callback = si_members.get(func_name)
            if callback is None:
                raise MethodNotFound()
            elif callable(callback):
                return service_instance, callback
            raise TypeError
        else:
            raise RuntimeError('No service instance found for %s.' % service_name)

service_container = ServiceContainer()

def decorator(func):
    @wraps(func)
    def entry_point(*args, **kwargs):
        return func(*args, **kwargs)
    return entry_point

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
        self.acceptor = None

    def publish(self, service_cls, method):
        assert inspect.isclass(service_cls)
        self.service_name = service_cls.__dict__.get('name')
        self.method_name = method.__name__
        service_instance = service_cls()
        method = decorator(method)
        service_container.add_service(self.service_name, service_instance, method)
        self.__register(self.service_name, self.method_name)
        self.__expose_service()

    def __register(self, service_name, method_name):
        '''
        rst = {
            status : 0 | -1,
            message : "register to xxx successfully..."
        }
        '''
        routing_key = "api/service/register"
        body = {
            "service_ip" : get_host_ip(),
            "service_port" : self.broker_port,
            "service_name" : service_name,
            "method_name" : method_name
        }
        rst = self.__post_request(routing_key, body)
        if handle_result(rst):
            print ('register service - %s into registry center success...' % service_name)
        else:
            service_container.del_service(service_name, method_name)
            print ('register service - %s into registry center failure...' % service_name)
            raise rst['result']
        


    def  __expose_service(self):
        print ('publish remote method - %s for service - %s on port - %d' % (self.method_name, \
                    self.service_name, int(self.broker_port)))
        self.acceptor = Bio_Acceptor(self.broker_port)
        self.acceptor.set_defaults()
        self.acceptor.request_handler = _ClientRequestHandler.handle_request_data
        self.acceptor.serve_forever()

    def __unregister_service(self, service_name, method_name):
        routing_key = "api/service/unregister"
        body = {
            "service_name" : service_name,
            "method_name" : method_name
        }
        rst = self.__post_request(routing_key, body)

    def __post_request(self, routing_key, body):
        assert isinstance(body, dict)
        registry_info = self.registry_url.split("://")
        endpoint = registry_info[0], (registry_info[1].split(":"))
        return make_request(endpoint, "POST", routing_key, body)

    def __handle_reply_msg(self, reply_msg):
        assert isinstance(reply_msg, dict)
        status = reply_msg['status']
        message = reply_msg['result']
        return status >= 0

class _ClientRequestHandler(object):

    @staticmethod
    def handle_request_data(payload):
        '''
        the format of payload should be like this:
        payload = {
            service_name : 'foo_service',
            method_name : 'bar_method',
            call_args : {
                args : [],
                kwargs : {}
            }
        }
        '''
        try:
            service_name = payload['service_name']
            method_name = payload['method_name']
            call_args = payload['call_args']
            service_instance, callback = service_container.lookup_serv(\
                service_name, method_name)
            args = call_args['args']
            kwargs = call_args['kwargs']
            _ClientRequestHandler.__check_signature(service_instance, \
                callback, *args, **kwargs)
            return _ClientRequestHandler.__reply_call_result(callback, \
                    service_instance, *args, **kwargs)
        except BaseException as exc:
            return _ClientRequestHandler.__reply_call_failure(exc)

    @staticmethod
    def __check_signature(service_instance, fn, *args, **kwargs):
        try:
            inspect.getcallargs(fn, service_instance, *args, **kwargs)
        except TypeError as exc:
            raise IncorrectSignature(str(exc))

    @staticmethod
    def __reply_call_failure(exc):
        return serialize(exc)

    @staticmethod
    def __reply_call_result(fn, instance, *args, **kwargs):
        return fn(instance, *args, **kwargs)
