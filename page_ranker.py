import threading
from queue import Queue, Empty

from utils import get_sub_domain_name


class PageRanker:
    def __init__(self, rank_queue: Queue):
        self.rank_queue = rank_queue
        self.rank_output = set()
        self.done_crawling = threading.Event()

    def rank(self):
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
        same_domain = 0
        different_domain = 0
        page_domain = get_sub_domain_name(page.url)
        for link in page.out_links:
            link_domain = get_sub_domain_name(link)
            if link_domain == page_domain:
                same_domain += 1
            else:
                different_domain += 1
        if same_domain == 0 and different_domain == 0:
            page.rank = 0
        else:
            page.rank = float("{:.2f}".format(same_domain/(different_domain + same_domain)))

    def print_ranks(self):
        for page in self.rank_output:
            print(page)
