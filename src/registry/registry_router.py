#!/usr/bin/python3.5
import os
import sys

sys.path.append('..')
from rpc_core.utils import parse_json_file
from rpc_core.utils import validate_args

class RegistryRouter(object):

    router_rules = None

    @staticmethod
    def init_routers():
        ''' initialize the router information from the router config files '''
        try:
            config_file = os.path.dirname(os.path.realpath(__file__)) + \
                '/registry_api.json'
            RegistryRouter.router_rules = parse_json_file(config_file)
        except BaseException as _be:
            raise RuntimeError('An error ocurred when parsing router-rule files.')

    @staticmethod
    def dispatch(routing_key, method="GET", **kwargs):
        '''dispatch the request according to routing key and requet method'''
        if not RegistryRouter.router_rules:
            raise RuntimeError('Router rules have not been initialized yet!')
        router_info = RegistryRouter.router_rules[routing_key]
        if not routing_key:
            raise RuntimeError('No routing info found for request tag: %s.' % \
                        routing_key)
        if method.upper() not in router_info:
            raise RuntimeError('No routing info found for request method: %s.' % \
                        method.upper())
        callback_info = router_info[method.upper()]
        assert isinstance(callback_info, dict)
        module_name = "registry_api"
        module = __import__("registry.%s" % module_name, fromlist='registry')
        if not module:
            raise RuntimeError('Module: %s imported error!' % module_name)
        for func_name, required_args in callback_info.items():
            break
        assert isinstance(required_args, str)
        required_args = required_args.split('|')
        if not validate_args(kwargs, required_args):
            raise RuntimeError('Request arguments is not valid!')
        callback = module.__dict__.get(func_name)
        print ("callback:\t", callback)
        if callback is None:
            raise RuntimeError('No callback function found for routing_key: %s.' % \
                        routing_key)
        elif not callable(callback):
            raise TypeError
        return callback(**kwargs)
