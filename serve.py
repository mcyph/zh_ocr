from os import listdir
from os.path import isdir
from json import dumps
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from get_L_tsv import Book
from consts import base_dir

from pyramid.view import (
    view_config,
    view_defaults
)

def get_L_books():
    LRtn = []

    for book_name in listdir(base_dir):
        if not isdir('%s/%s' % (base_dir, book_name)):
            continue
        LRtn.append(book_name)

    return LRtn

class TutorialViews:
    def __init__(self, request):
        self.request = request
        DBooks = self.DBooks = {}

        for book_name in get_L_books():
            DBooks[book_name] = Book(book_name)

    @view_config(route_name='browse',
                 renderer='static/browse.jinja2')
    def browse(self):
        LBooks = get_L_books()
        return {
            'LBooks': LBooks
        }

    @view_config(route_name='view_book',
                 renderer='static/base.jinja2')
    def view_book(self):
        book_name = self.request.matchdict['book_name'].replace('_', ' ')

        book = self.DBooks[book_name]
        LImages = book.get_L_tsv()

        return {
            'LImages': dumps(LImages),
            'title': book_name
        }

    @view_config(route_name='set_exception',
                 renderer='string')
    def set_exception(self):
        book_name = self.request.matchdict['book_name'].replace('_', ' ')
        hash_ = self.request.params['hash']
        orig_text = self.request.params['orig_text']
        new_text = self.request.params['new_text']

        book = self.DBooks[book_name]
        book.add_exception(hash_, orig_text, new_text)
        return 'OK'


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')

    config.add_route('browse', '/')
    config.add_route('view_book', '/{book_name}/')
    config.add_route('set_exception', '/{book_name}/set_exception')
    config.scan('serve')

    config.add_static_view(name='static', path='static')
    config.add_static_view(name='img', path='/home/david/Documents/Chinese textbooks/')

    return config.make_wsgi_app()


if __name__ == '__main__':
    app = main({})
    server = make_server('127.0.0.1', 9001, app)
    server.serve_forever()
