#!/usr/bin/python3.5
import sys

sys.path.append("..")

from rpc_core.exceptions import deserialize

from rpc_core.utils import make_request
from rpc_core.utils import rpc_call_request
from rpc_core.exceptions import BadRequest
from rpc_core.exceptions import RemoteError

'''
Client Usage:
rpc = RpcProxy(config={"registry_uri":"tcp://localhost:9999"})
rpc.hello_service.hello('shit')
'''
class RpcProxy(object):

    def __init__(self, config):
        assert isinstance(config, dict)
        self.registry_uri = config['registry_uri']

    def __getattr__(self, service_name):
        return ServiceProxy(service_name, self.registry_uri)

class ServiceProxy(object):

    def __init__(self, name, registry_uri):
        self.remote_service_uri = registry_uri + '/' + name

    def __getattr__(self, method_name):
        remote_method_uri = self.remote_service_uri + '/' +\
            method_name
        return MethodProxy(remote_method_uri)

class MethodProxy(object):

    def __init__(self, remote_method_uri):
        self.remote_method_uri = remote_method_uri
        self.service_name = None
        self.method_name = None
        self.broker_endpoint = None
        self.resolve_registry()
        print (remote_method_uri)

    def resolve_registry(self):
        registry_info = self.remote_method_uri.split("://")
        proto = registry_info[0]
        ip_info, self.service_name, self.method_name = \
                registry_info[1].split("/")
        ip, port = ip_info.split(":")
        body = {
            "service_name" : self.service_name,
            "method_name" : self.method_name
        }
        service_broker_uri = self.__get_lookup_service(proto, \
            ip, port, body)
        self.__resolve_remote_broker(service_broker_uri)

    def __get_lookup_service(self, proto, registry_ip, registry_port, body):
        endpoint = (proto, (registry_ip, registry_port))
        try:
            response = make_request(endpoint, method="GET", \
                routing_key="api/service/lookup", body=body)
            if 'status' in response:
                if response['status'] < 0:
                    raise BadRequest("Service lookup failure!")
                elif response['status'] == 0:
                    return response['result']
                elif response['status'] == 1:
                    return None
                else:
                    raise "Unknown error!"
            else:
                raise deserialize(response)
        except BadRequest as br:
            raise br
        else:
            raise RuntimeError("Service discovery failure!")
        
    def __resolve_remote_broker(self, service_broker_uri):
        service_broker_info = service_broker_uri.split('://')
        proto, (broker_ip, broker_port) = service_broker_info[0], \
                service_broker_info[1].split(':')
        self.broker_endpoint = (proto, (broker_ip, broker_port))


    def __call__(self, *args, **kwargs):
        return rpc_call_request(self.broker_endpoint, self.service_name, \
                self.method_name, args, kwargs)

rpc = RpcProxy(config={"registry_uri":"tcp://localhost:9999"})
print (rpc.hello_service.say_hello('shit'))