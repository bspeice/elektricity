from unittest import TestCase
import conf_parser


class TestBuild_configurator(TestCase):
    def test_build_configurator(self):
        try:
            # noinspection PyTypeChecker
            conf_parser.build_configurator(None)
            self.fail("Must have dictionary to set up configurator")
        except TypeError:
            pass