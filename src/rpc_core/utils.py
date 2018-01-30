#! /usr/bin/python3.5
import json

from rpc_core.exceptions import BadRequest
from rpc_core.codec.rpc_encoder import JSON_Encoder
from rpc_core.codec.rpc_decoder import JSON_Decoder
from rpc_core.transport.rpc_connector import Bio_Connector

def parse_json_file(config_file):
    with open(config_file) as json_config:
        config_items = json.load(json_config)
    return config_items

def validate_args(args, required_args):
    '''
    This function used to validate the request parameters.
    '''
    assert isinstance(required_args, list)
    if not required_args:
        return True
    else:
        if not args:
            return False
        assert isinstance(args, dict)
        recv_args = args.keys()
        for arg in required_args:
            if arg not in recv_args:
                return False
        return True

def base_request(endpoint, data):
    '''
    Base request framwork with default transport layer and encoder/decoder.
    '''
    assert isinstance(endpoint, tuple)
    proto, (ip, port) = endpoint
    if proto == 'tcp':
        with Bio_Connector(ip, port) as connector:
            connector.send_data(JSON_Encoder, data)
            return connector.recv_data(JSON_Decoder)
    else:
        raise BadRequest("Not supported!")

def make_request(endpoint, method, routing_key, body):
    '''
    Make a request with routing_key and body to remote endpoint.
    Request method - method should be GET/POST/PUT/DELETE.
    '''
    data = {
        "header" : {
            "routing_key" : routing_key,
            "request_method" : method
        },
        "body" : body
    }
    return  base_request(endpoint, data)

def rpc_call_request(endpoint, service_name, method_name, \
                        args, kwargs):
    data = {
        "service_name" : service_name,
        "method_name" : method_name,
        "call_args": {
            "args" : args,
            "kwargs" : kwargs
        }
    }
    return base_request(endpoint, data)
