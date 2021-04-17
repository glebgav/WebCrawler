import json
import os
from utils import CrawlerStorageManager


class Page:
    backup_page_counter = 0     # global counter for pages saved

    def __init__(self, root_url, url, out_links=None, depth=0, rank=0, valid_mime=True):
        self.root_url = root_url
        self.url = url
        self.out_links = out_links
        self.depth = depth
        self.rank = rank
        self.valid_mime = valid_mime

    def __getitem__(self, link):
        yield self.out_links[link]

    def __repr__(self):
        return str(f"{self.url}  {self.depth}  {self.rank}")

    @staticmethod
    def _get_json_file_name():
        res = f"{Page.backup_page_counter}.json"
        Page.backup_page_counter += 1
        return res

    def get_json_path(self):
        """
            return json for save_to_json_file method
        """
        return os.path.join(self.root_url, CrawlerStorageManager.BACKUP_PAGES_DIR_NAME, self._get_json_file_name())

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def save_to_json_file(self):
        with open(self.get_json_path(), 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    @staticmethod
    def restore_form_json_file(path: str):
        try:
            with open(path, 'r') as f:
                return Page.from_json(json.load(f))
        except:
            return None





