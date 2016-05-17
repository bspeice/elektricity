import argparse
from wsgiref.simple_server import make_server
from conf_parser import build_configuration
from os.path import expanduser, join


# noinspection PyUnresolvedReferences
def start_server(cmd_args: dict):
    try:
        server_conf, configurator = build_configuration(cmd_args.configuration)
        app = configurator.make_wsgi_app()
        server = make_server(cmd_args.host, cmd_args.port, app)

        server.serve_forever()
    except FileNotFoundError:
        print("Unable to find configuration file. Does {} exist?"
              .format(cmd_args.configuration))
    except AttributeError:
        print("Unable to parse configuration file. Is {} a valid YML file?"
              .format(cmd_args.configuration))
    except KeyError:
        print('Unable to parse configuration file. Is there a `podcasts`'
              'section?')


if __name__ == '__main__':
    default_rc = join(expanduser('~'), '.repodrc')
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', help='Run server in verbose mode')
    parser.add_argument('--port', type=int, default=10000,
                        help='Port to use when starting the server')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host address to start the server')
    parser.add_argument('--configuration', type=str, default=default_rc,
                        help='Configuration file to start the server')

    args = parser.parse_args()
    start_server(args)
