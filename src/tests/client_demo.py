#! /usr/bin/python3
import datetime
import sys
sys.path.append("..")
from consumer.rpc import RpcProxy
#147.128.85.135
rpc = RpcProxy(config={"registry_uri":"tcp://localhost:9999"})
rpc.hello_service.say_hello('foobar')