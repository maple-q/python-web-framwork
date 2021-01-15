#! /usr/bin/python
# coding: utf-8
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from tramp.tramp import Tramp, BaseController, register, r, Response


tramp = Tramp()


class UserController(BaseController):

    __prefix__ = '/user'

    @register('/login', method=['GET', 'POST'])
    def login(self, request):
        pass

    @register('/logout', method=['GET'])
    def logout(self, request):
        pass


class BookController(BaseController):

    __prefix__ = '/book'

    @register('/add', method=['POST'])
    def add_book(self, request):
        return 'add book'

    @register('/delete', method=['POST'])
    def delete_book(self, request):
        return 'delete book'

    @register('/update', method=['POST'])
    def update_book(self, request):
        return 'update book'

    @register('/query', method=['GET'])
    def query_book(self, request):
        return 'query books'


@tramp.before_request
def judge_user(request):
    return Response('Find Page')


@tramp.before_request
def judge_hello(request):
    response = Response('Sorry')
    response.set_status_code(404)

    return response


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 9000
    server = WSGIServer((host, port), WSGIRequestHandler)
    server.set_app(tramp)
    print('Server Listen at: {}:{}'.format(host, port))

    server.serve_forever()
