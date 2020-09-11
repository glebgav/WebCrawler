import logging
import os
import re
from urllib.parse import urlparse, quote_plus, unquote_plus

import colorlog
import requests
from log_utils.helper import LogHelper

utils_logger = logging.getLogger("WebCrawlerUtils")
color_handler = LogHelper.generate_color_handler()
formatter = colorlog.ColoredFormatter('{log_color}{name}: {levelname} {message}', style='{')
color_handler.setFormatter(formatter)
utils_logger.addHandler(color_handler)
utils_logger.setLevel('INFO')


def check_if_site_exists(site):
    try:
        request = requests.get(site)
    except requests.exceptions.ConnectionError:
        return False
    if request.status_code == 200:
        return True
    return False


def add_valid_protocol_prefix(url: str):
    """
        add https or http prefix to valid url , default return will be https

    """
    if not re.match('(?:http|https)://', url):

        http = 'http://{}'.format(url)
        https = 'https://{}'.format(url)
        if check_if_site_exists(https):
            return https
        elif check_if_site_exists(http):
            return http
        return None
    return url


# Get domain name (example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''


# Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''


class CrawlerStorageManager:

    @staticmethod
    def page_to_file(page):
        file_name = CrawlerStorageManager.format_url_to_file_name(page.url)
        file_path = os.path.join(page.root_url, file_name)

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                for link in sorted(page.out_links):
                    f.write(link + "\n")

    @staticmethod
    def create_project_folders(*args):
        for arg in args:
            if not os.path.exists(arg):
                logger.info('Creating directory ' + arg)
                os.makedirs(arg)

    @staticmethod
    def format_url_to_file_name(url: str):
        return quote_plus(url) + ".txt"

    @staticmethod
    def format_file_name_to_url(file_name: str):
        return unquote_plus(file_name).rstrip(".txt")

