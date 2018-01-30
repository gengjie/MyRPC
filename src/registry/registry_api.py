#!/usr/bin/python3.5
from registry_center import service_repo

def register(**kwargs):
    service_ip = kwargs.pop("service_ip")
    service_port = kwargs.pop("service_port")
    service_name = kwargs.pop("service_name")
    method_name = kwargs.pop("method_name")
    service_uri = 'tcp://%s:%d' % (service_ip, int(service_port))
    try:
        service_repo.add(service_name, method_name, service_uri)
        print (service_repo.registered_services)
    except BaseException as baseexc:
        return {'status' : -1, 'result' : baseexc}
    return {'status' : 0, 'result' : 'fuck!'}

def lookup(**kwargs):
    service_name = kwargs.pop("service_name")
    method_name = kwargs.pop("method_name")
    try:
        uri = service_repo.lookup(service_name, method_name)
        return {'status' : 0, 'result' : uri}
    except BaseException as _exec:
        return {'status' : -1, 'result' : _exec}
