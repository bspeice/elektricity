"""
Given a configuration file, set up everything needed to kick
off the server.
"""
from importlib import import_module
import yaml
from pyramid.config import Configurator

# Needed for import_module call
# noinspection PyUnresolvedReferences
import modules

# Hardcoded, need to look up from users $HOME later
file_loc = 'example_conf.yaml'


def build_configuration(conf=file_loc) -> Configurator:
    with open(conf) as conf_file:
        conf_dict = yaml.load(conf_file)
        server_conf = Configurator()
        for mountpoint, feed in conf_dict.items():
            feed_package = import_module('modules.' + feed['package'])
            feed_class = getattr(feed_package, feed['class'])
            feed_instance = feed_class(**feed['args'])

            server_conf.add_route(mountpoint, '/' + mountpoint + '/')
            server_conf.add_view(feed_instance.view, route_name=mountpoint)

        return server_conf
