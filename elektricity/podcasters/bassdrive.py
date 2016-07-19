"""
Podcast provider for the Bassdrive Archives
"""
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import unquote

import requests
from feedgen.feed import FeedGenerator
from pytz import UTC

from podcasters.base import BasePodcast


class BassdriveParser(HTMLParser):
    def error(self, message):
        return super().error(message)

    record_link_text = False
    link_url = ''

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.links = []

    def handle_starttag(self, tag, attrs):
        """
        If we find an 'a' tag, make sure that we record
        the next link we come across

        >>> b = BassdriveParser()
        >>> b.handle_starttag('a', (('href', 'something.mp3'),))
        >>> b.record_link_text
        True
        >>> b.link_url
        'something.mp3'
        """
        href = ''
        for attr, val in attrs:
            if attr == 'href':
                href = val

        if tag == 'a' and href.find('mp3') != -1:
            self.record_link_text = True
            self.link_url = href

    def handle_data(self, data):
        """
        If we receive a new link, record it if we're inside an `a` tag

        >>> b = BassdriveParser()
        >>> not b.get_links()
        True
        >>> b.handle_data("some_link")
        >>> not b.get_links()
        True
        >>> b.handle_starttag('a', [['href', 'something.mp3']])
        >>> b.handle_data("some text")
        >>> len(b.get_links()) == 1
        True
        """
        if self.record_link_text:
            self.links.append((data, self.link_url))
            self.record_link_text = False

    def get_links(self):
        # Reverse to sort in descending date order
        return self.links

    def clear_links(self):
        """
        For whatever reason, creating a new parser doesn't
        clear out the old links.

        >>> import requests
        >>> b = BassdriveParser()
        >>> b.feed(str(requests.get('http://archives.bassdrivearchive.com/' +\
            '1%20-%20Monday/Subfactory%20Show%20-%20DJ%20Spim').content))
        >>> len(b.get_links()) > 0
        True
        >>> b.clear_links()
        >>> len(b.get_links()) == 0
        True
        """
        self.links = []


class BassdriveFeed(BasePodcast):
    def __init__(self, *args, **kwargs):
        self.url = kwargs['url']
        self.logo = kwargs.get('logo', '')
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
        fg.id(self.url)
        fg.title(self.title)
        fg.description(self.title)
        fg.author({'name': self.dj})
        fg.language('en')
        fg.link({'href': self.url, 'rel': 'alternate'})
        fg.logo(self.logo)

        for link in links:
            fe = fg.add_entry()
            fe.author({'name': self.dj})
            fe.title(link[0])
            fe.description(link[0])
            fe.enclosure(self.url + link[1], 0, 'audio/mpeg')

            # Bassdrive always uses date strings of
            # [yyyy.mm.dd] with 0 padding on days and months,
            # so that makes our lives easy
            date_start = link[0].find('[')
            date_str = link[0][date_start:date_start+12]
            published = datetime.strptime(date_str, '[%Y.%m.%d]')
            fe.pubdate(UTC.localize(published))
            fe.guid((link[0]))

        return fg
