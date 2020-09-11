import optparse
import sys

from utils import get_domain_name, add_valid_protocol_prefix
from web_crawler import WebCrawler


INPUT_DEPTH_LIMIT = 40


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
                      action="store", type="int", default=5, dest="depth_limit",
                      help="Maximum depth to traverse")

    opts, args = parser.parse_args()

    if not opts.url:
        parser.print_help(sys.stderr)
        raise SystemExit(1)

    return opts, args


def web_crawler_main():
    opts, args = get_args()

    url = add_valid_protocol_prefix(opts.url)
    depth_limit = opts.depth_limit if 0 <= opts.depth_limit <= INPUT_DEPTH_LIMIT else None

    if url and depth_limit:
        domain_name = get_domain_name(url)
        web_crawler = WebCrawler(url, domain_name, depth_limit)
        web_crawler.start()

    else:
        if not url:
            print("invalid page address")
        if not depth_limit:
            print("invalid depth limit")
        raise SystemExit(1)


if __name__ == '__main__':
    web_crawler_main()
