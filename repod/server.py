from wsgiref.simple_server import make_server
from conf_parser import build_configuration

def start_server():
    app = build_configuration().make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

if __name__ == '__main__':
    start_server()
