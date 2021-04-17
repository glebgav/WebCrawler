import threading
from queue import Queue, Empty
from utils import get_sub_domain_name


class PageRanker:
    """
        class for calculation and presentation
        of simple rank for a given page
    """
    def __init__(self, rank_queue: Queue, logger):
        self.logger = logger
        self.rank_queue = rank_queue
        self.rank_output = set()    # set of all ranked Pages
        self.done_crawling = threading.Event()  # indicator when spiders done crawling

    def rank(self):
        """
            main method of PageRanker , get Pages from rank queue,
            rank them and store in a set.
            done when queue is empty and spiders are done crawling
        """
        while True:
            try:
                page = self.rank_queue.get_nowait()
                self.rank_page(page)
                self.rank_output.add(page)
                self.rank_queue.task_done()
            except Empty:
                if self.done_crawling.is_set():
                    break

    @staticmethod
    def rank_page(page):
        """
        calculates the ratio between same sub domain pages
        to different domain/sub domain.
        stores result in ratio attribute in Page object
        for later use.
        :param page: Page object
        """
        same_domain = 0
        different_domain = 0
        page_domain = get_sub_domain_name(page.url)
        for link in page.out_links:
            link_domain = get_sub_domain_name(link)
            if link_domain == page_domain:
                same_domain += 1
            else:
                different_domain += 1
        if not (same_domain == 0 and different_domain == 0):
            page.rank = float(f"{(same_domain/(different_domain + same_domain)):.3f}")

    def print_ranks(self):
        self.logger.info("Ranked Pages: \n\t\t\t\turl   depth   ratio")
        for page in self.rank_output:
            self.logger.info(page)
