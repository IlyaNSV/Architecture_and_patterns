from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
from datetime import date

from templator import render


class IndexPage:
    def __call__(self, request):
        return '200 OK', render('index.html', data=request.get('data', None))


class AboutPage:
    def __call__(self, request):
        return '200 OK', render('about.html', data=request.get('data', None))


class Page404:
    def __init__(self, path):
        self.path = path

    def __call__(self, request):
        if self.path[-1] != '/':
            return '404 WHAT', 'You forgot to put "/" in the end of url'
        return '404 WHAT', '404 PAGE not found'


routes = {
    '/': IndexPage(),
    '/about/': AboutPage(),
}


def secret_front(request):
    request['secret'] = 'some secret'


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]


class Framework:

    def __init__(self, routes, fronts):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        if path in self.routes:
            view = self.routes[path]
        else:
            view = Page404(path)
        request = {}

        for front in self.fronts:
            front(request)

        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]


application = Framework(routes, fronts)

with make_server('', 8000, application) as httpd:
    print("Serving on port 8000...")
    httpd.serve_forever()