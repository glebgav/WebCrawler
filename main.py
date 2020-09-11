import logging
import optparse
import sys
import colorlog
from log_utils.helper import LogHelper
from utils import get_domain_name, add_valid_protocol_prefix
from web_crawler import WebCrawler

logger = logging.getLogger("WebCrawler")
color_handler = LogHelper.generate_color_handler()
formatter = colorlog.ColoredFormatter('{log_color}{name}: {levelname} {message}', style='{')
color_handler.setFormatter(formatter)
logger.addHandler(color_handler)
logger.setLevel('DEBUG')
INPUT_DEPTH_LIMIT = 8


def get_args():
    """get_args() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """
    parser = optparse.OptionParser()

    parser.add_option("-u", "--url",
                      action="store", type="str", default=None, dest="url",
                      help="get root url")

    parser.add_option("-d", "--depth",
                      action="store", type="int", default=INPUT_DEPTH_LIMIT, dest="depth_limit",
                      help="Maximum depth to traverse")

    opts, _ = parser.parse_args()

    if not opts.url:
        parser.print_help(sys.stderr)
        raise SystemExit(1)

    return opts, _


def web_crawler_main():
    opts, args = get_args()

    url = add_valid_protocol_prefix(opts.url)
    depth_limit = opts.depth_limit if 0 <= opts.depth_limit <= INPUT_DEPTH_LIMIT else None

    if url and depth_limit:
        domain_name = get_domain_name(url)
        web_crawler = WebCrawler(url, domain_name, depth_limit, logger)
        web_crawler.start()

    else:
        if not url:
            logger.error("invalid page address")
        if not depth_limit:
            logger.error("invalid depth limit")
        raise SystemExit(1)


if __name__ == '__main__':
    web_crawler_main()
