#! /usr/bin/python
# coding: utf-8


class Tramp(object):
    """
    Tramp is a python web framework that implements wsgi protocol.
    Tramp Class is the interface between the web server and web framework, So when deploy your application,
    you can provide the Tramp Class to the server.
    """
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start_response(status, response_headers)
        yield b'Hello World, Tramp!'
