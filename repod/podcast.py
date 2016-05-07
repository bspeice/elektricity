"""
Base skeleton for what needs to be implemented by a podcast provider
"""
from feedgen.feed import FeedGenerator
from pyramid.response import Response


class BasePodcast():

    def build_feed(self) -> FeedGenerator:
        "Return a list of all episodes, in descending date order"
        pass

    def view(self, request):
        fg = self.build_feed()
        response = Response(fg.rss_str(pretty=True))
        response.content_type = 'application/rss+xml'
        return response
