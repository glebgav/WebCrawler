import concurrent
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from page import Page
from spider import Spider
from page_ranker import PageRanker
from utils import CrawlerStorageManager


class WebCrawler:
    """
    main class of the web crawler.
    this class responsible of orchestration of all
    workers and flows in web crawler app :
    """
    MAX_RANK_WORKERS = 3
    MAX_CRAWL_WORKERS = 12

    def __init__(self, root_url, domain_name: str, depth_limit: int, crawl_queue_time_out: int, logger):
        self.logger = logger
        self.root_url = root_url
        self.domain_name = domain_name
        self.depth_limit = depth_limit

        self.crawl_queue = Queue()                    # queue of tuples (url, depth) to crawl
        self.rank_queue = Queue()                     # queue of Pages to rank
        self.seen_urls = set()                        # all urls that have been seen (including not the right mime type)
        self.processed_urls = set()                   # all valid urls that have been processed
        self.spider_thread_futures = []               # futures of all spiders threads

        self.ranker = PageRanker(self.rank_queue, self.logger)
        self.spider = Spider(self.crawl_queue, self.seen_urls,
                             self.processed_urls, self.rank_queue, self.depth_limit, self.domain_name,
                             crawl_queue_time_out, self.logger)
        self.boot_with_root()

    def start(self):
        """
            1)start spider and ranker threads
            2)wait until spider threads are done
            3)wait until ranker threads are done
            4)print output of ranks
        """
        self.start_spider()
        self.start_ranker()

        concurrent.futures.wait(self.spider_thread_futures)     # wait for spiders to finish
        self.logger.info("Done crawling")
        self.ranker.done_crawling.set()

        self.ranker.print_ranks()

    def start_spider(self):
        self.logger.info("Starting to crawl..")
        executor = ThreadPoolExecutor(WebCrawler.MAX_CRAWL_WORKERS)
        for _ in range(WebCrawler.MAX_CRAWL_WORKERS):
            self.spider_thread_futures.append(executor.submit(self.spider.work))
        executor.shutdown(wait=False)

    def start_ranker(self):
        executor = ThreadPoolExecutor(WebCrawler.MAX_RANK_WORKERS)
        for _ in range(WebCrawler.MAX_RANK_WORKERS):
            executor.submit(self.ranker.rank)
        executor.shutdown(wait=False)

    def boot_with_root(self):
        """
            insert initial root url to crawl queue , if backup files exist , process them and
            add to appropriate queues and sets
        """
        CrawlerStorageManager.create_project_folders(self.domain_name,
                                                     os.path.join(self.domain_name,
                                                                  CrawlerStorageManager.BACKUP_PAGES_DIR_NAME))
        self.crawl_queue.put((self.root_url, 0))
        self.restore_state_from_disk()

    def restore_state_from_disk(self):
        """
            iterate over backup folder and:
                1)restore queues and sets from previous run
                2)update page counter
        """
        path = os.path.join(self.domain_name, CrawlerStorageManager.BACKUP_PAGES_DIR_NAME)
        if len(os.listdir(path)) > 0:
            self.logger.info("restoring data from previous session...")
            page_count = 0
            for subdir, dirs, files in os.walk(path):
                for file in files:
                    page_count += 1
                    abs_path = os.path.join(subdir, file)
                    page = Page.restore_form_json_file(abs_path)
                    if page:
                        self._add_page_to_queues_and_sets(page)
            Page.backup_page_counter = page_count

    def _add_page_to_queues_and_sets(self, page: Page):
        """
            following logic will apply:
            1)root url already in queue , don't process it.
            2)add every page url to seen urls set
            3)only if valid mime type:
                3.1) if current page depth is less then the limit , add his links to the crawl queue
                3.2)add to processed set and rank queue
        :param page: Page object that was restored from disk
        """
        if not page.url == self.root_url and page.url not in self.seen_urls:
            self.seen_urls.add(page.url)
            if page.valid_mime:
                if page.depth < self.depth_limit:
                    for link in page.out_links:
                        if not link == self.root_url:
                            self.crawl_queue.put((link, page.depth+1))
                self.processed_urls.add(page.url)
                self.rank_queue.put(page)


















