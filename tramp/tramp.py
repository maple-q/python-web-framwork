#! /usr/bin/python
# coding: utf-8
import functools

from collections import OrderedDict


DEFAULT_METHOD = 'GET'


class Tramp(object):
    """
    Tramp is a python web framework that implements wsgi protocol.
    Tramp Instance is the interface between the web server and web framework, So when deploy your application,
    you can provide the Tramp Instance to the server.
    """
    def __init__(self):
        # url map
        self.url_map = dict()

        # prefix map
        self.prefix_map = OrderedDict()

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)

        response = self.url_map[environ['PATH_INFO']]('')
        yield response.encode()


class Router(object):
    def __init__(self):
        """
        {
            "/user/login": {
                "method": ["GET", "POST],
                "view": view_function
            }
        }
        """
        self.route_map = OrderedDict()

    def add_url_rule(self, url, view_function, method):
        if url in self.route_map:
            raise Exception('Existing url: {}'.format(url))

        self.route_map[url] = view_function

    def __str__(self):
        router_size = len(self.route_map)
        routes = []

        for url in self.route_map:
            routes.append(url)

        return '<RouterSize: {}, Routers: {}>'.format(router_size, '[' + ', '.join(routes) + ']')


r = Router()


class MetaController(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'BaseController':
            return type.__new__(MetaController, name, bases, attrs)

        prefix = attrs.pop('__prefix__', None)
        if not prefix:
            prefix = '/'

        for name, value in attrs.items():
            if hasattr(value, 'url') and hasattr(value, 'method'):
                r.add_url_rule(prefix + getattr(value, 'url'), value, getattr(value, 'method'))

        return type.__new__(MetaController, name, bases, attrs)


class BaseController(metaclass=MetaController):
    pass


def register(url, method):
    def func(view):
        def inner(*args, **kwargs):
            view(*args, **kwargs)

        setattr(inner, 'url', url)
        setattr(inner, 'method', method)
        return inner

    return func
