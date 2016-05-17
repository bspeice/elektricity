import argparse
import traceback
from os.path import expanduser, join
from wsgiref.simple_server import make_server

from pyramid.config import Configurator

from conf_parser import build_configuration


# noinspection PyUnresolvedReferences
def start_server(server_conf: dict, configurator: Configurator) -> None:
    app = configurator.make_wsgi_app()

    port = server_conf['port'] if 'port' in server_conf else cmd_args.port
    host = server_conf['host'] if 'host' in server_conf else cmd_args.host
    server = make_server(host, port, app)

    server.serve_forever()

if __name__ == '__main__':
    default_rc = join(expanduser('~'), '.repodrc')
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true',
                        help='Run server in verbose mode')
    parser.add_argument('--port', type=int, default=10000,
                        help='Port to use when starting the server')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host address to start the server')
    parser.add_argument('--configuration', type=str, default=default_rc,
                        help='Configuration file to start the server')

    cmd_args = parser.parse_args()
    try:
        server_conf, configurator = build_configuration(cmd_args.configuration)
        start_server(server_conf, configurator)
    except FileNotFoundError:
        print("Unable to find configuration file. Does {} exist?"
              .format(cmd_args.configuration))
        if cmd_args.verbose:
            print(traceback.format_exc())
    except AttributeError:
        print("Unable to parse configuration file. Is {} a valid YML file?"
              .format(cmd_args.configuration))
        if cmd_args.verbose:
            print(traceback.format_exc())
    except KeyError:
        print('Unable to parse configuration file. Is there a `podcasts` '
              'section?')
        if cmd_args.verbose:
            print(traceback.format_exc())
