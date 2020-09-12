import logging
import optparse
import sys
import colorlog
from log_utils.helper import LogHelper
from utils import add_valid_protocol_prefix, get_sub_domain_name
from web_crawler import WebCrawler

DEFAULT__DEPTH_LIMIT = 2
DEFAULT_TIME_OUT = 30
DEFAULT_LOG_LEVEL = 'INFO'

"""
multi threaded Web Crawler app , with simple rank capabilities.

"""


def get_args():
    """get_args() -> opts, args

    Parse any command-line options given returning
    the parsed options.
    """
    parser = optparse.OptionParser()

    parser.add_option("-u", "--url",
                      action="store", type="str", default=None, dest="url",
                      help="get root url")

    parser.add_option("-d", "--depth",
                      action="store", type="int", default=DEFAULT__DEPTH_LIMIT, dest="depth_limit",
                      help="Maximum depth to traverse")

    parser.add_option("-t", "--time_out",
                      action="store", type="int", default=DEFAULT_TIME_OUT, dest="time_out",
                      help="time out value for spiders in case of empty queue")

    opts, _ = parser.parse_args()

    if not opts.url:
        parser.print_help(sys.stderr)
        raise SystemExit(1)

    return opts, _


def get_logger():
    logger = logging.getLogger("WebCrawler")
    color_handler = LogHelper.generate_color_handler()
    formatter = colorlog.ColoredFormatter('{log_color}{name}: {levelname} {message}', style='{')
    color_handler.setFormatter(formatter)
    logger.addHandler(color_handler)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    return logger


def web_crawler_main():
    """
        check user input and start WebCrawler
    """
    opts, args = get_args()
    logger = get_logger()

    url = add_valid_protocol_prefix(opts.url)
    depth_limit = opts.depth_limit if 0 < opts.depth_limit <= DEFAULT__DEPTH_LIMIT else None
    time_out = opts.time_out if 0 < opts.time_out else None

    if not url or not depth_limit or not time_out:
        if not url:
            logger.error("invalid page address")
        if not depth_limit:
            logger.error("invalid depth limit")
        if not time_out:
            logger.error("invalid time out")
        raise SystemExit(1)

    domain_name = get_sub_domain_name(url)
    web_crawler = WebCrawler(url, domain_name, depth_limit, time_out, logger)
    web_crawler.start()


if __name__ == '__main__':
    web_crawler_main()
