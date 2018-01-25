#! /user/bin/python3.5
from registry_router import RegistryRouter

class RemoteServiceHandler:

    @staticmethod
    def handle_request_data(payload):
        assert isinstance(payload, dict)
        routing_key = payload['header']['routing_key']
        request_method = payload['header']['request_method']
        args = payload['body']
        return RegistryRouter.dispatch(routing_key, request_method, args)

class ClientRequestHandler:
    pass
        