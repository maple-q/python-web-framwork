#! /usr/bin/python
# coding: utf-8
import os

from collections import OrderedDict

DEFAULT_METHOD = 'GET'
STATUS_CODE_MAP = {
    200: 'OK',
    404: 'Not Found.',
    500: 'Server Error.'
}


class Request(object):
    """
    根据web server传过来的environ构造请求对象
    暂时只取需要的数据
    """

    def __init__(self, environ):
        self.environ = environ

        # 请求的content-length
        self.content_length = self.environ['CONTENT_LENGTH']

        # 请求的远程host
        self.remote_host = self.environ['REMOTE_HOST']

        # 请求参数
        self.query_string = self.environ['QUERY_STRING']

        # 请求的path
        self.path_info = self.environ['PATH_INFO']

        # 远程地址
        self.remote_addr = self.environ['REMOTE_ADDR']

        # User-Agent，可以初过滤一些低级的爬虫
        self.user_agent = self.environ['HTTP_USER_AGENT']

        # 请求方法
        self.request_method = self.environ['REQUEST_METHOD']

        # cookie信息
        self.cookie = self.environ['HTTP_COOKIE']

        self.parse_query()

    def parse_query(self):
        """
        解析请求参数
        :return:
        """
        pass


class Response(object):
    """
    响应对象，支持返回字符串、html文件
    """

    def __init__(self, string, template_name=None, render_template=False):
        self.string = string

        # 状态码，默认200
        self.status_code = 200
        # 状态码描述
        self.status_desc = STATUS_CODE_MAP.get(self.status_code)

        # 响应头部
        self.headers = {}

        # 如果用户使用模板方式填充响应，则读取模板文件内容
        if render_template:
            self.string = self.render_template(template_name)

    def set_status_code(self, status_code):
        if not isinstance(status_code, int):
            raise Exception('status code must be int type!')

        if STATUS_CODE_MAP.get(status_code, None) is None:
            raise Exception('Invalid status code!')

        self.status_code = status_code
        self.status_desc = STATUS_CODE_MAP.get(self.status_code)

    def set_headers(self, header_dict):
        if not isinstance(header_dict, dict):
            raise Exception('header dict must be dict type!')

        self.headers.update(header_dict)

    def get_status_code(self):
        return self.status_code

    def get_status_desc(self):
        return self.status_desc

    def render_template(self, template_name):
        """
        读取模板html文件并返回
        :param template_name: 模板文件
        :return:
        """
        if not template_name:
            raise Exception('Empty template name!')

        if not os.path.exists(template_name):
            raise Exception('template: {} is not exists!'.format(template_name))

        template_content = ''
        try:
            with open(template_name, 'rb') as f:
                template_content = f.read()
        except Exception:
            print('read template file: {} failed!'.format(template_name))

        return template_content

    def format_response_header(self):
        """
        组装headers，最后需要返回给服务器
        :return:
        """
        response_header = list()

        for header_key, header_value in self.headers.items():
            response_header.append((header_key, header_value))

        return response_header

    def format_response_body(self):
        """
        响应体编码判断
        :return:
        """
        if type(self.string) == bytes:
            return self.string

        elif type(self.string) == str:
            return self.string.encode('utf-8')

        else:
            raise Exception('Unsupported response body type: {}!'.format(type(self.string)))


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

        # 请求hook列表，在请求到达视图函数之前执行，存放可调用对象列表
        self.pre_process_list = list()

        # 响应hook列表，在视图函数处理完之后执行，存放可调用对象列表
        self.post_process_list = list()

    def __call__(self, environ, start_response):
        # 创建请求对象
        request = Request(environ)

        # 先过请求hook，请求钩子函数默认返回None，支持返回Response对象，如果返回None，则走下一个钩子函数
        # 如果返回Response对象，则直接返回
        for pre_view_function in self.pre_process_list:
            response = pre_view_function(request)
            if not response:
                continue

            if not isinstance(response, Response):
                raise Exception('request hook function must return None or Response object!')

            # 返回response对象，则直接返回响应
            response_body = self.response_to_server(response, environ, start_response)
            yield response_body

        # TODO 搜索视图函数进行处理，得到Response对象

        # 过响应hook列表

        # 返回响应

    def response_to_server(self, response, environ, start_response):
        """
        设置状态码，响应头信息，调用start_response方法，并返回响应
        :param response: Response对象
        :param environ:
        :param start_response:
        :return:
        """
        status = '{} {}'.format(response.get_status_code(), response.get_status_desc())
        response_headers = response.format_response_header()
        start_response(status, response_headers)

        # 返回响应
        return response.format_response_body()

    def before_request(self, func):
        if not callable(func):
            raise Exception('func: {} is not callable!'.format(func))

        self.pre_process_list.append(func)

        def inner(*args, **kwargs):
            func(*args, **kwargs)

        return inner

    def after_request(self, func):
        if not callable(func):
            raise Exception('func: {} is not callable!'.format(func))

        self.post_process_list.append(func)

        def inner(*args, **kwargs):
            func(*args, **kwargs)

        return inner


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

    def add_url_rule(self, url, view_function, method, class_name):
        if url in self.route_map:
            raise Exception('Existing url: {}'.format(url))

        self.route_map[url] = {
            'method': method,
            'view': view_function,
            'instance': class_name()
        }

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

        class_obj = type.__new__(MetaController, name, bases, attrs)
        for name, value in attrs.items():
            if hasattr(value, 'url') and hasattr(value, 'method'):
                r.add_url_rule(prefix + getattr(value, 'url'), value, getattr(value, 'method'), class_obj)

        return class_obj


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
