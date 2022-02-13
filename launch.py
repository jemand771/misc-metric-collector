from wsgiref.simple_server import make_server

from main import app

httpd = make_server('', 9125, app)
httpd.serve_forever()
