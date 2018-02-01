# MyRPC
## myrpc is a simple lightweight RPC framwork for python language, which is used to validata how to implement a rpc framework in python.
### Usage for myrpc:
1. start myrpc registry center:
2. service provider:
```python
class HelloService:
    name = "hello_service"

    def say_hello(self, name):
        return "Hello, %s!" % name

service_broker = ServiceBroker("tcp://localhost:9999", 7777)
service_broker.publish(HelloService, HelloService.say_hello)
```
2. service consumer:
```python
rpc = RpcProxy(config={"registry_uri":"tcp://localhost:9999"})
rpc.hello_service.say_hello('foobar')
```
