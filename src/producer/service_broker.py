#! /usr/bin/python
import threading
import inspect

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
        assert inspect.ismethod(func)
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

    def lookup_serv(self, service, func_name):
        if isinstance(service, str):
            if self.service_instances.has_key(service):
                si_info = self.service_instances.get(service)
                assert isinstance(si_info, dict)
                for si, si_members in si_info:
                    break
                assert isinstance(si_members, dict)
                callback = si_members.get(func_name)
                if not callback or not callable(callback):
                    return callback
                raise TypeError
            else:
                raise RuntimeError('No service instance found for %s.' % service)
        elif inspect.isclass(service):
            pass

service_container = ServiceContainer()

class ServiceBroker:

    def __init__(self, tcp_port):
        self.tcp_port = tcp_port

    def publish(self, service_cls, method):
        assert inspect.isclass(service_cls)
        assert inspect.ismethod(method)
        service_name = service_cls.__dict__.get('name')
        service_instance = service_cls()
        service_container.add_service(service_name, service_instance, method)
        

    def register(self, service_name, method_name):
        pass