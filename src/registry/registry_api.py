#!/usr/bin/python3.5

def register(args):
    print('enter register...')
    print (args)
    return {'status' : 0, 'result' : 'fuck!'}

def lookup(args):
    print ('enter lookup')
    print (args)
    return {'status' : 0, 'result' : 'tcp://localhost:7777'}