"""
Given a configuration file, set up everything needed to kick
off the server.
"""
from importlib import import_module

import yaml
from pyramid.config import Configurator


def build_configurator(podcasts: dict) -> Configurator:
    server_conf = Configurator()
    for mountpoint, feed in podcasts:
        package, class_name = feed['class'].rsplit('.', 1)
        feed_package = import_module(package)
        feed_class = getattr(feed_package, class_name)
        feed_instance = feed_class(**feed['args'])

        server_conf.add_route(mountpoint, '/' + mountpoint + '/')
        server_conf.add_view(feed_instance.view, route_name=mountpoint)


def build_configuration_text(file_str: str) -> (dict, Configurator):
    conf_dict = yaml.load(file_str)

    server_opts = conf_dict.get('server', None)
    podcasts = build_configurator(conf_dict['podcasts'])
    return server_opts, podcasts


def build_configuration(file_name) -> (dict, Configurator):
    try:
        with open(file_name) as conf_file:
            return build_configuration_text(conf_file.read())
    except FileNotFoundError:
        print("Could not locate configuration file " +
              "(does {} exist?)".format(file_name))
        raise
