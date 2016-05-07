"""
Podcast provider for the Bassdrive Archives
"""
from html.parser import HTMLParser
from urllib.parse import unquote

import requests
from feedgen.feed import FeedGenerator

from podcast import BasePodcast


class BassdriveParser(HTMLParser):
    links = []
    record_link_text = False
    link_url = ''

    def handle_starttag(self, tag, attrs):
        href = ''
        for attr, val in attrs:
            if attr == 'href':
                href = val

        if tag == 'a' and href.find('mp3') != -1:
            self.record_link_text = True
            self.link_url = href

    def handle_data(self, data):
        if self.record_link_text:
            print(self.link_url)
            self.links.append((data, self.link_url))
            self.record_link_text = False

    def get_links(self):
        # Reverse to sort in descending date order
        self.links.reverse()
        return self.links


class BassdriveFeed(BasePodcast):
    def __init__(self, *args, **kwargs):
        print(kwargs)
        self.url = kwargs['url']
        # Get the title and DJ while handling trailing slash
        url_pretty = unquote(self.url)
        elems = filter(lambda x: x, url_pretty.split('/'))
        self.title, self.dj = list(elems)[-1].split(' - ')

    def build_feed(self):
        "Build the feed given our existing URL"
        # Get all the episodes
        page_content = str(requests.get(self.url).content)
        parser = BassdriveParser()
        parser.feed(page_content)
        links = parser.get_links()

        # And turn them into something usable
        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.id(self.url)
        fg.title(self.title)
        fg.description(self.title)
        fg.author({'name': self.dj})
        fg.language('en')
        fg.link({'href': self.url, 'rel': 'alternate'})

        for link in links:
            fe = fg.add_entry()
            fe.author({'name': self.dj})
            fe.title(link[0])
            fe.description(link[0])
            fe.enclosure(self.url + link[1], 0, 'audio/mpeg')

        return fg
