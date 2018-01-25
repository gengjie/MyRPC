#! /usr/bin/python3.5
import json
class BaseDecoder:

    @staticmethod
    def decode(raw):
        pass

class JSON_Decoder(BaseDecoder):

    @staticmethod
    def decode(raw):
        if isinstance(raw, bytes):
            raw = str(raw, encoding="utf8")
        return json.loads(raw)
