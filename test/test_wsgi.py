#! /usr/bin/python
# coding: utf-8
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from tramp.tramp import Tramp


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 9000
    server = WSGIServer((host, port), WSGIRequestHandler)
    server.set_app(Tramp)
    print('Server Listen at: {}:{}'.format(host, port))

    server.serve_forever()
