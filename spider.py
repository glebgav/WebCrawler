import threading
from queue import Queue
from link_finder import LinkFinder, IncorrectMimeType
from page import Page
from utils import CrawlerStorageManager


class Spider:
    seen_urls_lock = threading.RLock()
    processed_urls_lock = threading.RLock()

    def __init__(self, crawl_queue: Queue, seen_urls: set, processed_urls: set, rank_queue: Queue
                 , depth_limit, domain_name, logger):
        self.logger = logger
        self.crawl_queue = crawl_queue
        self.seen_urls = seen_urls
        self.processed_urls = processed_urls
        self.rank_queue = rank_queue
        self.depth_limit = depth_limit
        self.domain_name = domain_name

        self.link_finder = LinkFinder(self.logger)

    def work(self):
        while True:
            url, depth = self.crawl_queue.get(timeout=30)
            self.crawl_queue.task_done()
            try:
                if depth <= self.depth_limit:
                    with Spider.seen_urls_lock:
                        seen_already = url in self.seen_urls
                    if not seen_already:
                        page, links = self.crawl_page(url, depth, self.domain_name)
                        self._add_links_to_crawl_queue(links, depth)
                        self._add_page_to_rank_queue(page, url)
                    with Spider.seen_urls_lock:
                        self.seen_urls.add(url)
            except Exception as e:
                self.logger.debug(e)

    def _add_links_to_crawl_queue(self, links, depth):
        if links and depth < self.depth_limit:
            for link in links:
                with Spider.seen_urls_lock:
                    if link in self.seen_urls:
                        continue
                    else:
                        self.crawl_queue.put((link, depth + 1))

    def _add_page_to_rank_queue(self, page, url):
        with Spider.processed_urls_lock:
            if page and url not in self.processed_urls:
                self.rank_queue.put(page)
                self.processed_urls.add(url)

    def crawl_page(self, url: str, depth: int, domain_name: str):
        """
            crawl a given url (if it's valid)
            save it to disk and return set of out links and the Page object
        :rtype: Page, set()
        """
        self.logger.debug("crawling {} in depth {}".format(url, depth))
        try:

            links = self.link_finder.fetch_links(url)
            page = Page(domain_name, url, links, depth)
            page.save_to_json_file()
            CrawlerStorageManager.page_to_file(page)
            if links:
                return page, links
        except IncorrectMimeType:
            self.logger.debug("incorrect mime type")
            page = Page(domain_name, url, [], depth, valid_mime=False)
            page.save_to_json_file()
        return None, None







