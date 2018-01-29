#!/usr/bin/python3.5
'''
Client Usage:
rpc = RpcProxy(config={"registry_uri":"tcp://localhost:9999"})
rpc.hello_service.hello('shit')

'''

class RemoteProxy(object):

    def __init__(self, cls):
        pass