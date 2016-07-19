"""
Given a configuration file, set up everything needed to kick
off the server.
"""
from importlib import import_module
import yaml
from pyramid.config import Configurator
from os.path import expanduser, join

# Needed for import_module call
# noinspection PyUnresolvedReferences
import podcasters


def build_configuration(conf=None) -> Configurator:
    if conf is None:
        conf = join(expanduser('~'), '.repodrc')

    server_conf = Configurator()
    with open(conf) as conf_file:
        conf_dict = yaml.load(conf_file)
        for mountpoint, feed in conf_dict.items():
            feed_package = import_module('podcasters.' + feed['package'])
            feed_class = getattr(feed_package, feed['class'])
            feed_instance = feed_class(**feed['args'])

            server_conf.add_route(mountpoint, '/' + mountpoint + '/')
            server_conf.add_view(feed_instance.view, route_name=mountpoint)

    return server_conf
