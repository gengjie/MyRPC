#! /usr/bin/python3
import sys
sys.path.append("..")

from producer.service_broker import ServiceBroker

class HelloService:
    name = "hello_service"

    def say_hello(self, name):
        return "Hello, %s!" % name

service_broker = ServiceBroker("tcp://localhost:9999", 7777)
service_broker.publish(HelloService, HelloService.say_hello)
