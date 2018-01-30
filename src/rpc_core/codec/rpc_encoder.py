#! /usr/bin/python3.5
import json

class BaseEncoder(object):

    @staticmethod
    def encode_data(obj):
        pass


class JSON_Encoder(BaseEncoder):

    @staticmethod
    def encode_data(obj):
        json_str = json.dumps(obj, default=lambda _obj: _obj.__dict__)
        json_str += '\n'
        return bytes(json_str, encoding="utf8")

class Protobuf_Encoder(BaseEncoder):
    pass