import sys
import urllib.parse
from urllib.request import urlopen
from html import escape
from bs4 import BeautifulSoup


class IncorrectMimeType(Exception):
    pass


class LinkFinder:
    def __init__(self, logger):
        self.logger = logger

    def fetch_links(self, url):
        """
        fetch all out links from url if they are from
        :param url: str of url
        :return: set of out links from input url text/html mime_type
        """
        out_links = set()
        content = ''
        try:
            response = urlopen(url)
            if 'text/html' not in response.getheader('Content-Type'):
                raise IncorrectMimeType
            html_bytes = response.read()
            content = html_bytes.decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")
            tags = soup('a')
        except Exception as e:
            self.logger.debug(sys.stderr, "ERROR: %s" % e)
            tags = []
        for tag in tags:
            href = tag.get("href")
            if href:
                parsed_url = urllib.parse.urljoin(url, escape(href))
                out_links.add(parsed_url)
        return list(out_links)

