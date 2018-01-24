#! /usr/bin/python3.5
import json

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
