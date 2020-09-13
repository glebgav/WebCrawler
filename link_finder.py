import urllib.parse
from urllib.request import urlopen
from html import escape
from bs4 import BeautifulSoup


class IncorrectMimeType(Exception):
    pass


class LinkFinder:
    VALID_MIME_TYPE = "text/html"

    @staticmethod
    def fetch_links(url):
        """
        fetch all out links from url if they are from
        :param url: str of url
        :return: set of out links from input url text/html mime_type
        """
        out_links = set()
        content = ''
        try:
            with urlopen(url) as response:
                if response.info().get_content_type() != LinkFinder.VALID_MIME_TYPE:
                    raise IncorrectMimeType
                html_bytes = response.read()

            content = html_bytes.decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")
            tags = soup('a')
        except IncorrectMimeType:
            raise IncorrectMimeType
        except Exception as e:
            raise e
        for tag in tags:
            href = tag.get("href")
            if href:
                parsed_url = urllib.parse.urljoin(url, escape(href))
                out_links.add(parsed_url)
        return list(out_links)

